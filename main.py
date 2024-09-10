import sys
import time
import tracemalloc
from typing import Callable
from src.simulator import simulation_hanoi
from src.hanoi_states import StatesHanoi, ProblemHanoi
from src.tree_hanoi import NodeHanoi
from src.search import (
    breadth_first_tree_search,
    breadth_first_graph_search
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
        
        # TODO: Insert data in DB for futher analysis
        return result
    return wrapper

@metrics
def execute_algorithm(problem_hanoi: ProblemHanoi, solver: Callable) ->  NodeHanoi:
    # Resuelve el problema utilizando búsqueda en anchura
    # Esta forma de búsqueda es muy ineficiente, por lo que si deseas probarlo, usa 3 discos o si querés esperar
    # un poco más, 4 discos, pero 5 discos no finaliza nunca.
    #last_node = breadth_first_tree_search(problem_hanoi)
    # Resuelve el problema utilizando búsqueda en anchura, pero con memoria que recuerda caminos ya recorridos.
    last_node = solver(problem_hanoi, display=True)
    return last_node

def solve_problem(name: str, problem_hanoi: ProblemHanoi, solver: Callable) -> None:
    print(f'-'*50)
    print(f'Solving problem using {name}')
    
    last_node = execute_algorithm(problem_hanoi, breadth_first_graph_search)

    if isinstance(last_node, NodeHanoi):
        # Imprime la longitud del camino de la solución encontrada
        print(f'Longitud del camino de la solución: {last_node.state.accumulated_cost}')

        # Genera los JSON para el simulador
        last_node.generate_solution_for_simulator()
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
    # Define el estado inicial y el estado objetivo del problema
    initial_state = StatesHanoi([5, 4, 3, 2, 1], [], [], max_disks=5)
    goal_state = StatesHanoi([], [], [5, 4, 3, 2, 1], max_disks=5)

    # Crea una instancia del problema de la Torre de Hanoi
    problem_hanoi = ProblemHanoi(initial=initial_state, goal=goal_state)

    problems = {
        'breadth_first_tree_search': breadth_first_tree_search,
        'breadth_first_graph_search2': breadth_first_graph_search
    }
        
    for name, search in problems.items():
        solve_problem(name, problem_hanoi, search)
        

if __name__ == "__main__":
    """
    Sección de ejecución del programa
    """
    
    if sys.argv[1] == "solve":
        main()
        
    if sys.argv[1] == "simulate":
        simulate()
