"""
=========================================================
Enterprise AI Business Decision Intelligence Platform
Base AI Agent
Author : Feroz Ali
=========================================================
"""


class BaseAgent:


    def __init__(self, name: str):

        self.name = name



    # ============================================
    # Agent Information
    # ============================================

    def info(self):

        return {

            "agent": self.name,

            "status": "Ready"

        }



    # ============================================
    # Execute Task
    # ============================================

    def execute(self, task):

        raise NotImplementedError(
            f"{self.name} must implement execute() method."
        )