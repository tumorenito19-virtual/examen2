import heapq
import json
import os
from datetime import datetime

class TaskManager:
    def __init__(self, data_file="tasks.json"):
        self.tasks = []  # Heap para manejar las tareas
        self.completed_tasks = []  # Lista para manejar las tareas completadas
        self.data_file = data_file
        self.load_tasks()

    def add_task(self, name, priority, dependencies, due_date):
        if not name or not isinstance(priority, int):
            raise ValueError("El nombre de la tarea no puede estar vacío y la prioridad debe ser un número entero.")
        
        task = {
            "name": name,
            "priority": priority,
            "dependencies": dependencies,
            "due_date": due_date,
        }
        heapq.heappush(self.tasks, (priority, due_date, task))
        self.save_tasks()

    def show_tasks(self):
        print("Tareas pendientes en orden de prioridad:")
        if not self.tasks:
            print("No hay tareas pendientes.")
        else:
            for _, _, task in sorted(self.tasks):
                print(f"Tarea: {task['name']}, Prioridad: {task['priority']}, Fecha de vencimiento: {task['due_date']}, Dependencias: {', '.join(task['dependencies'])}")

    def complete_task(self):
        if not self.tasks:
            print("No hay tareas para completar.")
            return
        
        priority, due_date, task = heapq.heappop(self.tasks)
        if not self._are_dependencies_completed(task):
            print(f"No se puede completar la tarea '{task['name']}' porque sus dependencias no están completadas.")
            heapq.heappush(self.tasks, (priority, due_date, task))
            return

        self.completed_tasks.append(task)
        print(f"Tarea completada: {task['name']}")
        self.save_tasks()

    def complete_specific_task(self, task_name):
        for i, (priority, due_date, task) in enumerate(self.tasks):
            if task["name"] == task_name:
                if not self._are_dependencies_completed(task):
                    pending_deps = [dep for dep in task['dependencies'] if dep not in [t['name'] for t in self.completed_tasks]]
                    print(f"Error: No se puede completar la tarea '{task['name']}' porque las siguientes dependencias no están completadas: {', '.join(pending_deps)}.")
                    return
                self.completed_tasks.append(task)
                del self.tasks[i]
                heapq.heapify(self.tasks)  # Reorganizar el heap
                print(f"Tarea completada: {task['name']}")
                self.save_tasks()
                return
        print(f"No se encontró la tarea con el nombre '{task_name}'.")

    def _are_dependencies_completed(self, task):
        completed_task_names = [t["name"] for t in self.completed_tasks]
        return all(dep in completed_task_names for dep in task["dependencies"])

    def get_next_task(self):
        if not self.tasks:
            print("No hay tareas disponibles.")
            return None
        
        _, _, task = self.tasks[0]
        print(f"Siguiente tarea: {task['name']}, Prioridad: {task['priority']}, Fecha de vencimiento: {task['due_date']}")
        return task

    def show_completed_tasks(self):
        print("Tareas completadas:")
        if not self.completed_tasks:
            print("No hay tareas completadas.")
        else:
            for task in self.completed_tasks:
                print(f"Tarea: {task['name']}, Fecha de vencimiento: {task['due_date']}, Dependencias: {', '.join(task['dependencies'])}")

    def save_tasks(self):
        with open(self.data_file, "w") as f:
            json.dump({
                "pending_tasks": [task for _, _, task in self.tasks],
                "completed_tasks": self.completed_tasks
            }, f, indent=4)

    def load_tasks(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for task in data.get("pending_tasks", []):
                            heapq.heappush(self.tasks, (task["priority"], task["due_date"], task))
                        self.completed_tasks = data.get("completed_tasks", [])
                    else:
                        print("El archivo JSON no tiene la estructura esperada. Se inicializarán datos vacíos.")
                except json.JSONDecodeError:
                    print("Error al decodificar el archivo JSON. Se inicializarán datos vacíos.")

if __name__ == "__main__":
    manager = TaskManager()

    # Crear lista de tareas inicial
    initial_tasks = [
        {"name": "Tarea 1", "priority": 1, "dependencies": ["Tarea 3"], "due_date": "2024-12-15"},
        {"name": "Tarea 2", "priority": 3, "dependencies": [], "due_date": "2024-12-20"},
        {"name": "Tarea 3", "priority": 2, "dependencies": [], "due_date": "2024-12-18"},
        {"name": "Tarea 4", "priority": 5, "dependencies": ["Tarea 2", "Tarea 3"], "due_date": "2024-12-25"},
    ]

    for task in initial_tasks:
        manager.add_task(task["name"], task["priority"], task["dependencies"], task["due_date"])

    while True:
        print("\nGestor de Tareas")
        print("1. Añadir nueva tarea")
        print("2. Mostrar todas las tareas")
        print("3. Completar tarea de mayor prioridad")
        print("4. Obtener siguiente tarea de mayor prioridad")
        print("5. Ver tareas completadas")
        print("6. Completar tarea específica")
        print("7. Salir")
        
        choice = input("Selecciona una opción: ")

        if choice == "1":
            name = input("Nombre de la tarea: ")
            priority = int(input("Prioridad de la tarea (número entero, menor es más importante): "))
            dependencies = input("Dependencias (separadas por comas): ").split(',')
            due_date = input("Fecha de vencimiento (YYYY-MM-DD): ")
            try:
                datetime.strptime(due_date, "%Y-%m-%d")  # Validar formato de fecha
                manager.add_task(name, priority, dependencies, due_date)
                print("Tarea añadida con éxito.")
            except ValueError:
                print("Formato de fecha inválido.")

        elif choice == "2":
            manager.show_tasks()

        elif choice == "3":
            manager.complete_task()

        elif choice == "4":
            manager.get_next_task()

        elif choice == "5":
            manager.show_completed_tasks()

        elif choice == "6":
            task_name = input("Nombre de la tarea que deseas completar: ")
            manager.complete_specific_task(task_name)

        elif choice == "7":
            print("Saliendo del gestor de tareas.")
            break

        else:
            print("Opción inválida. Intenta de nuevo.")
