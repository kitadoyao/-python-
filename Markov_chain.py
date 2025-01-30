import random
from typing import List, Tuple
class Markov_chain:
    def __init__(self, edges:List[Tuple[str, str, float]]):
        self._states=self._add_states(edges)
        self._P=self._build_P(edges, self._states)
    def _add_states(self, edges):
        states=set()
        for state_0, state_1, cpd in edges:
            states.update([state_0,state_1])
        return list(states)
    def _build_P(self, edges, states):
        P = [[0] * len(states) for _ in range(len(states))]
        for state in states:
            if sum([cpd for state_0, _, cpd in edges if state_0 == state]) != 1:
                raise ValueError(f"This state lacks data or data redundancy: {state}")
            if any(not (0<cpd<=1) for state_0, state_1, cpd in edges if state_0 == state):
                raise ValueError(f"Out of range (0, 1] : ({state_0}, {state_1}, {cpd})")
        for state_0, state_1, cpd in edges:
            P[states.index(state_0)][states.index(state_1)] = cpd
        return P
    def random_walk(self, state:str, time:int):
        if state not in self._states:
            raise ValueError(f"Not in the graph : {state}")
        if time <= 0:
            raise ValueError("Meaningless parameters")
        num=len(self._states)
        current = state
        path = []
        for _ in range(time):
            idx_0 = self._states.index(current)
            idxs = []
            probs = []
            for idx, prob in zip(range(num), self._P[idx_0]):
                if prob != 0:
                    idxs.append(idx)
                    probs.append(prob)
            if not probs:
                break
            idx_1 = random.choices(idxs, probs)[0]
            path.append(self._states[idx_1])
            current = path[-1]
        return path
    def predict(self, state:str, time:int):
        if state not in self._states:
            raise ValueError(f"Not in the graph : {state}")
        if time <= 0:
            raise ValueError("Meaningless parameters")
        v_0 = [(0 if idx != self._states.index(state) else 1) for i in range(len(self._P))]
        P_n = Matrix_Operations._pow(self._P, time)
        v_1 = [sum(v_0[i]*P_n[i][j] for i in range(len(P))) for j in range(len(P))]
        return v_1