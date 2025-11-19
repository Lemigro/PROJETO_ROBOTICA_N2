"""
Robô Aspirador Inteligente - Arquivo Principal
Sistema completo de simulação, mapeamento e aprendizado
"""
import pybullet as p
import pybullet_data
import time
import numpy as np
import os
import argparse

from src.robot import VacuumRobot
from src.sensors import SensorArray
from src.controller import ObstacleAvoidanceController, ExplorationController
from src.mapping import OccupancyMap
from src.learning import RouteOptimizer
from src.logger import NodeREDLogger, MetricsCollector
from src.environment import VacuumEnvironment


class VacuumRobotSimulation:
    """Simulação completa do robô aspirador"""
    
    def __init__(self, gui=True, load_map=False, map_file="map.json", execution_number=1):
        """
        Inicializa a simulação
        
        Args:
            gui: Se True, mostra interface gráfica
            load_map: Se True, carrega mapa anterior
            map_file: Arquivo do mapa
            execution_number: Número da execução (para aprendizado)
        """
        # Conecta ao PyBullet
        if gui:
            self.physics_client = p.connect(p.GUI)
        else:
            self.physics_client = p.connect(p.DIRECT)
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        
        # Configurações da simulação
        p.setTimeStep(1./240.)  # 240 Hz
        p.setRealTimeSimulation(0)  # Step-by-step
        
        # Cria ambiente
        self.environment = VacuumEnvironment(self.physics_client, add_obstacles=True)
        
        # Cria robô
        start_pos = [0, 0, 0.1]
        start_orientation = [0, 0, 0]
        self.robot = VacuumRobot(self.physics_client, start_pos, start_orientation)
        
        # Cria sensores
        self.sensors = SensorArray(self.physics_client, num_sensors=5, max_range=2.0)
        
        # Cria controladores
        avoidance_controller = ObstacleAvoidanceController(
            safe_distance=0.3,
            max_speed=2.5,
            max_angular_speed=3.0
        )
        self.controller = ExplorationController(avoidance_controller)
        
        # Cria mapa
        self.map = OccupancyMap(
            width=40,
            height=40,
            resolution=0.1,
            origin_x=-2,
            origin_y=-2
        )
        
        # Carrega mapa anterior se solicitado
        # Tenta primeiro no diretório maps/, depois no caminho fornecido
        if load_map:
            map_path = map_file
            if not os.path.isabs(map_file) and not os.path.exists(map_file):
                # Tenta no diretório maps/
                map_path = os.path.join("maps", map_file)
            
            if os.path.exists(map_path):
                if self.map.load(map_path):
                    print(f"Mapa carregado de {map_path}")
            else:
                print(f"Aviso: Arquivo de mapa nao encontrado: {map_file}")
        
        # Sistema de aprendizado
        self.optimizer = RouteOptimizer()
        
        # Logger (Node-RED)
        self.logger = NodeREDLogger(node_red_url="http://127.0.0.1:1880", use_mqtt=False)
        
        # Coletor de métricas
        self.metrics = MetricsCollector()
        self.metrics.start()
        
        # Estado da simulação
        self.running = True
        self.execution_number = execution_number
        self.simulation_time = 0.0
        self.max_simulation_time = 300.0  # 5 minutos máximo
        
        # Controle de passo
        self.step_count = 0
        self.log_interval = 10  # Log a cada 10 passos
        
        # Rastreamento de energia para cálculo de delta
        self.last_energy = 0.0
    
    def run(self):
        """Executa a simulação principal"""
        print("=== Iniciando Simulação do Robô Aspirador ===")
        print(f"Execução #{self.execution_number}")
        print("Pressione Ctrl+C para parar")
        
        try:
            while self.running and p.isConnected():
                # Passo da simulação
                p.stepSimulation()
                
                # Obtém pose do robô
                x, y, yaw = self.robot.get_pose()
                
                # Lê sensores
                sensor_readings = self.sensors.read_all(
                    self.robot.robot_id,
                    [x, y, 0.1],
                    yaw
                )
                
                # Atualiza mapa de ocupação
                sensor_angles = [0, -np.pi/4, np.pi/4, -np.pi/2, np.pi/2]
                self.map.update_occupancy(x, y, sensor_readings, sensor_angles, yaw)
                
                # Atualiza cobertura
                dt = 1./240.
                self.map.update_coverage(x, y, dt)
                
                # Adiciona ponto à trajetória
                if self.step_count % 5 == 0:  # A cada 5 passos
                    self.map.add_trajectory_point(x, y, yaw)
                
                # Obtém sugestões de otimização
                suggestions = self.optimizer.get_optimization_suggestions(self.map)
                
                # Calcula velocidade (passa sugestões de otimização)
                linear, angular = self.controller.compute_velocity(
                    sensor_readings,
                    (x, y, yaw),
                    coverage_map=self.map if self.execution_number > 1 else None,
                    optimization_suggestions=suggestions if self.execution_number > 1 else None
                )
                
                # Aplica velocidade ao robô
                self.robot.set_velocity(linear, angular)
                
                # Atualiza energia
                self.robot.update_energy(dt)
                
                # Calcula incremento de energia
                energy_delta = self.robot.energy_consumed - self.last_energy
                self.last_energy = self.robot.energy_consumed
                
                # Verifica colisão
                collision = self.environment.check_collision(self.robot.robot_id)
                
                # Atualiza métricas
                self.metrics.update([x, y], energy_delta, collision)
                
                # Calcula cobertura (usado para logs e condições de parada)
                coverage_pct = self.map.get_coverage_percentage()
                
                # Log periódico
                if self.step_count % self.log_interval == 0:
                    # Log de trajetória
                    self.logger.log_trajectory_point(x, y, yaw, sensor_readings)
                    
                    # Log de métricas
                    metrics = self.metrics.get_metrics(coverage_pct)
                    self.logger.log_metrics(metrics)
                    
                    # Print no console
                    if self.step_count % 100 == 0:
                        print(f"Tempo: {self.simulation_time:.1f}s | "
                              f"Cobertura: {coverage_pct:.1f}% | "
                              f"Energia: {self.robot.energy_consumed:.2f}J | "
                              f"Colisões: {self.metrics.collisions}")
                
                # Atualiza tempo
                self.simulation_time += dt
                self.step_count += 1
                
                # Condições de parada
                if self.simulation_time >= self.max_simulation_time:
                    print("Tempo máximo de simulação atingido")
                    break
                
                if coverage_pct >= 95.0 and self.simulation_time > 10:
                    print("Área totalmente coberta!")
                    break
                
                # Sleep para visualização
                time.sleep(1./240.)
        
        except KeyboardInterrupt:
            print("\nSimulação interrompida pelo usuário")
        
        finally:
            self.finish()
    
    def finish(self):
        """Finaliza a simulação e salva dados"""
        print("\n=== Finalizando Simulação ===")
        
        # Calcula métricas finais
        coverage_pct = self.map.get_coverage_percentage()
        final_metrics = self.metrics.get_metrics(coverage_pct)
        
        # Adiciona ao histórico de aprendizado
        self.optimizer.add_execution(
            self.map.trajectory,
            coverage_pct,
            self.simulation_time,
            self.robot.energy_consumed
        )
        
        # Log de resumo
        summary = {
            'execution_number': self.execution_number,
            'coverage_percentage': coverage_pct,
            'total_time': self.simulation_time,
            'total_energy': self.robot.energy_consumed,
            'collisions': self.metrics.collisions,
            'trajectory_length': self.metrics.trajectory_length,
            'efficiency': final_metrics['efficiency'],
            'trajectory_points': len(self.map.trajectory)
        }
        
        self.logger.log_execution_summary(summary)
        
        # Salva mapa
        import os
        os.makedirs("maps", exist_ok=True)
        map_file = f"maps/map_exec_{self.execution_number}.json"
        self.map.save(map_file)
        print(f"Mapa salvo em {map_file}")
        
        # Estatísticas de aprendizado
        if self.execution_number > 1:
            improvement = self.optimizer.get_efficiency_improvement()
            print("\n=== Melhoria de Eficiência ===")
            print(f"Redução de tempo: {improvement['time_reduction']:.1f}%")
            print(f"Redução de energia: {improvement['energy_reduction']:.1f}%")
            print(f"Melhoria de eficiência: {improvement['improvement']:.4f}")
        
        # Print métricas finais
        print("\n=== Métricas Finais ===")
        print(f"Cobertura: {coverage_pct:.2f}%")
        print(f"Tempo total: {self.simulation_time:.2f}s")
        print(f"Energia consumida: {self.robot.energy_consumed:.2f}J")
        print(f"Colisões: {self.metrics.collisions}")
        print(f"Eficiência: {final_metrics['efficiency']:.4f} %/J")
        
        # Desconecta
        if p.isConnected():
            p.disconnect()
        
        print("Simulação finalizada!")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Robô Aspirador Inteligente')
    parser.add_argument('--no-gui', action='store_true', help='Executa sem interface gráfica')
    parser.add_argument('--load-map', action='store_true', help='Carrega mapa anterior')
    parser.add_argument('--map-file', type=str, default='map.json', help='Arquivo do mapa')
    parser.add_argument('--execution', type=int, default=1, help='Número da execução')
    
    args = parser.parse_args()
    
    # Cria e executa simulação
    sim = VacuumRobotSimulation(
        gui=not args.no_gui,
        load_map=args.load_map,
        map_file=args.map_file,
        execution_number=args.execution
    )
    
    sim.run()


if __name__ == "__main__":
    main()

