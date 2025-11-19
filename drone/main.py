"""
Script principal para simulação do drone de entregas.
"""
import yaml
import numpy as np
import time
import os
from pathlib import Path

from src.drone_simulator import DroneSimulator
from src.pid_controller import DroneController
from src.sensor import ProximitySensor
from src.route_planner import RoutePlanner
from src.logger import SimulationLogger


def load_config(config_path: str = "config/config.yaml") -> dict:
    """Carrega configurações do arquivo YAML."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def main():
    """Função principal da simulação."""
    # Carregar configurações
    config = load_config()
    
    # Criar diretório de logs se não existir
    log_dir = Path(config['logging'].get('file', 'logs/drone_simulation.log')).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Inicializar componentes
    simulator = DroneSimulator(config)
    # Mesclar configurações de controle e drone
    control_config = config['control'].copy()
    control_config.update({
        'max_velocity': config['drone']['max_velocity'],
        'max_acceleration': config['drone']['max_acceleration']
    })
    controller = DroneController(control_config)
    sensor = ProximitySensor(config['sensor']['detection_radius'])
    route_planner = RoutePlanner(config['route_planning'])
    logger = SimulationLogger(config['logging'])
    
    # Estado da simulação
    base_position = np.array(config['simulation']['base_position'])
    current_route = []
    current_target = None
    last_replan_time = time.time()
    replan_interval = config['route_planning'].get('replan_interval', 1.0)
    
    # Modo de patrulha: se não há pontos detectados, começar a patrulhar
    patrol_mode = True
    patrol_target = None
    
    # Variáveis de controle
    running = True
    step_count = 0
    last_sensor_update = 0
    sensor_update_rate = config['sensor'].get('update_rate', 10)
    sensor_update_interval = 1.0 / sensor_update_rate
    
    print("=" * 60)
    print("DRONE DE ENTREGAS - SIMULAÇÃO INICIADA")
    print("=" * 60)
    print(f"Pontos de entrega: {len(simulator.get_all_delivery_points())}")
    print(f"Raio de detecção: {config['sensor']['detection_radius']}m")
    print(f"Algoritmo de rota: {config['route_planning']['algorithm']}")
    print("=" * 60)
    
    try:
        while running:
            # Atualizar estado do drone
            simulator.step_simulation()
            drone_pos = simulator.position
            drone_vel = simulator.velocity
            drone_attitude = simulator.get_euler_angles()
            
            current_time = time.time()
            dt = simulator.timestep
            
            # Atualizar detecção de pontos (a uma taxa menor)
            if current_time - last_sensor_update >= sensor_update_interval:
                all_points = simulator.get_all_delivery_points()
                detected = sensor.detect_points(drone_pos, all_points)
                
                # Registrar novas detecções
                for point in detected:
                    if not hasattr(point, '_logged') or not point._logged:
                        logger.log_detection(point, drone_pos)
                        point._logged = True
                
                last_sensor_update = current_time
            
            # Verificar se chegou ao ponto atual
            if (current_target is not None and 
                sensor.check_delivery(
                    drone_pos,
                    current_target,
                    config['route_planning']['min_distance_threshold']
                )):
                logger.log_delivery(current_target, drone_pos)
                simulator.update_point_visualization(current_target, delivered=True)
                current_target = None
            
            # Replanejamento
            undelivered_points = sensor.get_undelivered_points()
            
            # Replanejar se:
            # 1. Não há rota atual
            # 2. Rota atual está vazia (todos entregues)
            # 3. Passou tempo suficiente desde último replanejamento
            should_replan = (
                not current_route or
                all(p.delivered for p in current_route) or
                (current_time - last_replan_time >= replan_interval and undelivered_points)
            )
            
            if should_replan and undelivered_points:
                # Replanejar rota
                current_route = route_planner.plan_route(
                    drone_pos,
                    undelivered_points,
                    base_position,
                    return_to_base=True
                )
                
                if current_route:
                    logger.log_replan(current_route, reason="periodic_update")
                    simulator.draw_route(current_route, drone_pos)
                    last_replan_time = current_time
            
            # Obter próximo alvo
            if current_target is None and current_route:
                current_target = route_planner.get_next_target(drone_pos, current_route)
                if current_target is None:
                    # Remover pontos entregues da rota
                    current_route = [p for p in current_route if not p.delivered]
                    if current_route:
                        current_target = route_planner.get_next_target(drone_pos, current_route)
            
            # Calcular controle
            if current_target is not None:
                # Ir ao ponto de entrega (velocidade normal)
                # Primeiro ir horizontalmente, depois descer para entregar
                horizontal_dist = np.linalg.norm(drone_pos[:2] - current_target.position[:2])
                if horizontal_dist > 1.0:
                    # Ainda longe horizontalmente: manter altura de voo
                    target_pos = np.array([current_target.position[0], current_target.position[1], drone_pos[2]])
                else:
                    # Próximo horizontalmente: descer para entregar (altura do ponto + 0.5m)
                    target_pos = np.array([
                        current_target.position[0], 
                        current_target.position[1], 
                        current_target.position[2] + 0.5
                    ])
                patrol_mode = False
                # Usar velocidade normal para entrega
                controller.set_speed_multiplier(1.0)
            elif undelivered_points:
                # Se há pontos detectados mas não entregues, ir ao mais próximo (velocidade normal)
                nearest_point = min(undelivered_points, 
                                  key=lambda p: np.linalg.norm(drone_pos[:2] - p.position[:2]))
                target_pos = np.array([nearest_point.position[0], nearest_point.position[1], drone_pos[2]])
                patrol_mode = False
                # Usar velocidade normal para ir ao ponto detectado
                controller.set_speed_multiplier(1.0)
            elif patrol_mode:
                # Modo patrulha: mover-se em padrão circular para detectar pontos
                # Usar raio maior baseado no tamanho da área
                import math
                area_size = config['environment'].get('area_size', [50, 50])
                max_radius = min(area_size) / 2.0  # Metade do menor lado da área
                patrol_radius = min(max_radius, 20.0)  # Máximo de 20m
                
                if patrol_target is None or np.linalg.norm(drone_pos[:2] - patrol_target[:2]) < 2.0:
                    # Criar novo alvo de patrulha (círculo ao redor da base)
                    # Usar ângulo que aumenta mais devagar para patrulha mais eficiente
                    angle_step = 0.2  # Graus por frame (reduzido para movimento mais lento)
                    angle = (step_count * angle_step) % 360 * math.pi / 180.0
                    patrol_target = np.array([
                        base_position[0] + patrol_radius * math.cos(angle),
                        base_position[1] + patrol_radius * math.sin(angle),
                        drone_pos[2]  # Manter altura atual
                    ])
                target_pos = patrol_target
                # Reduzir velocidade durante patrulha (50% da velocidade normal)
                controller.set_speed_multiplier(0.5)
            else:
                # Se não há alvo, retornar à base
                target_pos = base_position
                if np.linalg.norm(drone_pos[:2] - base_position[:2]) < 1.0:
                    patrol_mode = True  # Reativar patrulha se estiver na base
                    # Reduzir velocidade durante patrulha
                    controller.set_speed_multiplier(0.5)
                else:
                    # Velocidade normal para retornar à base
                    controller.set_speed_multiplier(1.0)
            
            force, torque = controller.compute_control(
                drone_pos,
                target_pos,
                drone_vel,
                drone_attitude,
                dt
            )
            
            # Debug: imprimir forças periodicamente
            if step_count % 240 == 0:  # A cada segundo
                print(f"Drone pos: {drone_pos}, Target: {target_pos}")
                print(f"Force: {force}, Torque: {torque}")
                print(f"Velocity: {drone_vel}")
                print(f"Altitude error: {target_pos[2] - drone_pos[2]:.3f}m")
                print(f"Force Z (thrust): {force[2]:.2f}N (should be ~9.81N for hover)")
                print("---")
            
            # Aplicar controle
            simulator.apply_control(force, torque)
            
            # Atualizar visualização
            simulator.draw_target_marker(target_pos if current_target is not None else None)
            
            # Logging periódico
            if step_count % 100 == 0:  # A cada ~0.4s (100 steps * 1/240s)
                logger.log_state(
                    drone_pos,
                    drone_vel,
                    target_pos if current_target is not None else None,
                    current_route,
                    sensor.get_all_detected()
                )
            
            # Verificar condição de término
            all_delivered = all(p.delivered for p in simulator.get_all_delivery_points())
            at_base = np.linalg.norm(drone_pos - base_position) < 1.0
            
            if all_delivered and at_base:
                print("\n" + "=" * 60)
                print("TODAS AS ENTREGAS CONCLUÍDAS!")
                print("=" * 60)
                time.sleep(2)
                running = False
            
            step_count += 1
            
            # Limitar tempo de simulação (segurança)
            if step_count > 1000000:  # ~1 hora de simulação
                print("Tempo máximo de simulação atingido")
                running = False
    
    except KeyboardInterrupt:
        print("\nSimulação interrompida pelo usuário")
    
    finally:
        # Finalizar
        logger.close()
        simulator.close()
        
        # Exibir métricas finais
        metrics = logger.get_metrics_summary()
        print("\n" + "=" * 60)
        print("MÉTRICAS FINAIS")
        print("=" * 60)
        print(f"Tempo total: {metrics['elapsed_time']:.2f}s")
        print(f"Distância total: {metrics['total_distance']:.2f}m")
        print(f"Replanejamentos: {metrics['replan_count']}")
        print(f"Pontos detectados: {metrics['points_detected']}")
        print(f"Pontos entregues: {metrics['points_delivered']}")
        print(f"Tempo médio por entrega: {metrics['avg_delivery_time']:.2f}s")
        print(f"Eficiência: {metrics['efficiency']:.2%}")
        print("=" * 60)


if __name__ == "__main__":
    main()

