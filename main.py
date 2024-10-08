import sys
import time
import tracemalloc
from datetime import datetime
from typing import Callable
from src.simulator import simulation_hanoi
from src.hanoi_states import StatesHanoi, ProblemHanoi
from src.models.metrics import Metrics
from src.services.databases import DatabaseService
from src.tree_hanoi import NodeHanoi
from src.search import (
    breadth_first_tree_search,
    breadth_first_graph_search,
    astar_search_heuristic1,
    astar_search_heuristic2,
    astar_search_heuristic3,
    greedy_search_heuristic1,
    greedy_search_heuristic2,
    greedy_search_heuristic3
)


def metrics(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # Start the timer
        tracemalloc.start()
        explored = None
        frontier = None

        result = func(*args, **kwargs)  # Call the original function
        if isinstance(result, tuple):
            explored = result[1]
            frontier = result[2]
            result = result[0]

        end_time = time.perf_counter()  # Stop the timer
        _, memory_peak = tracemalloc.get_traced_memory()
        memory_peak /= 1024*1024
        tracemalloc.stop()
        execution_time = end_time - start_time
        
        print(f"Tiempo que demoró {func.__name__}: {execution_time:4f} [s]", )
        print(f"Maxima memoria ocupada: {round(memory_peak, 2)} [MB]", )
        
        if 'db' in sys.argv[1]:
            db = DatabaseService()           
            db.add(Metrics(
                model_name=args[0],  # Add the model name as a parameter
                disks=args[1],
                timestamp=datetime.now(),
                memory_allocation=memory_peak,
                execution_time=execution_time,
                movements = explored,
                frontiers = frontier,
                cost = result.state.accumulated_cost,
                comments="",
            ))
            
        
        # TODO: Insert data in DB for futher analysis
        return result
    return wrapper

@metrics
def execute_algorithm(name: str, disks: int, problem_hanoi: ProblemHanoi, solver: Callable) ->  NodeHanoi:
    # Resuelve el problema utilizando búsqueda en anchura
    # Esta forma de búsqueda es muy ineficiente, por lo que si deseas probarlo, usa 3 discos o si querés esperar
    # un poco más, 4 discos, pero 5 discos no finaliza nunca.
    #last_node = breadth_first_tree_search(problem_hanoi)
    # Resuelve el problema utilizando búsqueda en anchura, pero con memoria que recuerda caminos ya recorridos.
    last_node_info = solver(problem_hanoi, display=True)
    return last_node_info

def solve_problem(name: str, disks: int, problem_hanoi: ProblemHanoi, solver: Callable) -> None:
    """
    Función que resuelve el problema de la Torre de Hanoi utilizando un algoritmo de búsqueda.

    Args:
        name (str): Nombre del algoritmo a utilizar
        problem_hanoi (ProblemHanoi): Instancia del problema de la Torre de Hanoi
        solver (Callable): Algoritmo de búsqueda a utilizar
    """
    print(f'-'*50)
    print(f'Solving problem using {name} and {disks} disks')
    
    last_node = execute_algorithm(name, disks, problem_hanoi, solver)

    if isinstance(last_node, NodeHanoi):
        # Imprimimos la longitud del camino de la solución encontrada
        print(f'Longitud del camino de la solución: {last_node.state.accumulated_cost}')

        # Genera los JSON para el simulador
        last_node.generate_solution_for_simulator(
            initial_state_file=f"./src/simulator/solutions/initial_state_{name}.json",
            sequence_file=f"./src/simulator/solutions/sequence_{name}.json"
        )
    else:
        print(last_node)
        print("No se encuentra solución")
        
def simulate() -> None:
    """
    Función que simula la solución del problema de la Torre de Hanoi.
    """
    simulation_hanoi.main()

def main(disks: int = 5, iterate: None|int = None) -> None:
    """
    Función principal que resuelve el problema de la Torre de Hanoi y genera los JSON para el simulador.
    Si iterate es None, corre el problema con la cantidad de discos especificada.
    Si es diferente de None, corre el problema con la cantidad de discos especificada en el rango de 3 a iterate.
    """
    if iterate is None:
        # Definimos estado inicial y estado final del problema a resolver
        initial_state = StatesHanoi(list(range(disks,0,-1)), [], [], max_disks=disks)
        goal_state = StatesHanoi([], [], list(range(disks,0,-1)), max_disks=disks)

        # Se crea una instancia del problema de la Torre de Hanoi
        problem_hanoi = ProblemHanoi(initial=initial_state, goal=goal_state)

        # Se resuelve el problema utilizando diferentes algoritmos de búsqueda
        problems = {
            'breadth_first_graph_search': breadth_first_graph_search,
            'astar_search_heuristic1': astar_search_heuristic1,
            'astar_search_heuristic2': astar_search_heuristic2,
            'astar_search_heuristic3': astar_search_heuristic3,
            'greedy_search_heuristic1': greedy_search_heuristic1,
            'greedy_search_heuristic2': greedy_search_heuristic2,
            'greedy_search_heuristic3': greedy_search_heuristic3
        }

        # Se resuelve el problema para cada algoritmo de búsqueda
        for name, search in problems.items():
            solve_problem(name, disks, problem_hanoi, search)
        # Definimos estado inicial y estado final del problema a resolver
    elif '-m' in sys.argv[1]:
        for i in range(3, int(iterate)+1):
            for j in range(10): # Se ejecuta 10 veces para obtener un promedio por cada modelo por cada valor de discos
                disks = i
                state = list(range(i,2,-1)) + [2, 1]
                initial_state = StatesHanoi(state, [], [], max_disks=disks)
                goal_state = StatesHanoi([], [], state, max_disks=disks)
                # Se crea una instancia del problema de la Torre de Hanoi
                problem_hanoi = ProblemHanoi(initial=initial_state, goal=goal_state)

                # Se resuelve el problema utilizando diferentes algoritmos de búsqueda
                problems = {
                    'breadth_first_graph_search': breadth_first_graph_search,
                    'astar_search_heuristic1': astar_search_heuristic1,
                    'astar_search_heuristic2': astar_search_heuristic2,
                    'astar_search_heuristic3': astar_search_heuristic3,
                    'greedy_search_heuristic1': greedy_search_heuristic1,
                    'greedy_search_heuristic2': greedy_search_heuristic2,
                    'greedy_search_heuristic3': greedy_search_heuristic3
                }

                # Se resuelve el problema para cada algoritmo de búsqueda
                for name, search in problems.items():
                    solve_problem(name, disks, problem_hanoi, search)

if __name__ == "__main__":
    """
    Sección de ejecución del programa
    """
    disks = int(sys.argv[2]) if len(sys.argv) > 2 else 5 
    
    if sys.argv[1] == "solve":
        main(disks)
    
    if sys.argv[1] == "solve-db":
        DatabaseService.init_database()
        main(disks)
        
    if sys.argv[1] == "simulate":
        simulate()

    if sys.argv[1] == "solve-db-m":
        DatabaseService.init_database()
        main(iterate=int(sys.argv[2]))