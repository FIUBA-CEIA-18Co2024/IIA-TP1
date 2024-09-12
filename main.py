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
    astar_search
)


def metrics(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # Start the timer
        tracemalloc.start()
        
        result = func(*args, **kwargs)  # Call the original function
        
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
    last_node = solver(problem_hanoi, display=True)
    return last_node

def solve_problem(name: str, disks: int, problem_hanoi: ProblemHanoi, solver: Callable) -> None:
    """
    Función que resuelve el problema de la Torre de Hanoi utilizando un algoritmo de búsqueda.

    Args:
        name (str): Nombre del algoritmo a utilizar
        problem_hanoi (ProblemHanoi): Instancia del problema de la Torre de Hanoi
        solver (Callable): Algoritmo de búsqueda a utilizar
    """
    print(f'-'*50)
    print(f'Solving problem using {name}')
    
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

def main() -> None:
    """
    Función principal que resuelve el problema de la Torre de Hanoi y genera los JSON para el simulador.
    """
    # Definimos estado inicial y estado final del problema a resolver
    disks = 8
    initial_state = StatesHanoi([8, 7, 6, 5, 4, 3, 2, 1], [], [], max_disks=disks)
    goal_state = StatesHanoi([], [], [8, 7, 6, 5, 4, 3, 2, 1], max_disks=disks)

    # Se crea una instancia del problema de la Torre de Hanoi
    problem_hanoi = ProblemHanoi(initial=initial_state, goal=goal_state)

    # Se resuelve el problema utilizando diferentes algoritmos de búsqueda
    problems = {
        #'breadth_first_tree_search': breadth_first_tree_search,
        'breadth_first_graph_search': breadth_first_graph_search,
        'astar_search': astar_search
    }
        
    # Se resuelve el problema para cada algoritmo de búsqueda
    for name, search in problems.items():
        solve_problem(name, disks, problem_hanoi, search)
        

if __name__ == "__main__":
    """
    Sección de ejecución del programa
    """
    
    if sys.argv[1] == "solve":
        main()
    
    if sys.argv[1] == "solve-db":
        DatabaseService.init_database()
        main()
        
    if sys.argv[1] == "simulate":
        simulate()
