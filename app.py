# app.py

import warnings
from typing import List, Dict, Any

import numpy as np
from flask import Flask, render_template, request, url_for

# Initialisation de l'application Flask
app = Flask(__name__)

def simplexe(c: List[float], A: List[List[float]], b: List[float]) -> Dict[str, Any]:
    """
    Résout un problème de programmation linéaire sous forme standard (maximisation)
    en utilisant l'algorithme du simplexe.
    """
    # Ignorer les avertissements de division par zéro qui peuvent survenir
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    try:
        c_np = np.array(c, dtype=float)
        A_np = np.array(A, dtype=float)
        b_np = np.array(b, dtype=float)
        
        n_vars = len(c_np)
        m_constr = len(b_np)
        
        # Création du tableau initial avec les variables d'écart
        slack_vars = np.eye(m_constr)
        tableau = np.hstack((A_np, slack_vars, b_np.reshape(-1, 1)))
        
        # Ajout de la ligne de la fonction objectif (Z) - CHANGED: removed negative sign
        z_row = np.hstack((c_np, np.zeros(m_constr + 1)))
        tableau = np.vstack((tableau, z_row))
        
        initial_tableau = np.copy(tableau)
        
        iteration_limit = 1000
        iterations = 0

        # NEW: Store pivot history
        pivot_history = []

        # Phase 2 de l'algorithme du simplexe - CHANGED: conditions for maximization
        while np.max(tableau[-1, :-1]) > 1e-6 and iterations < iteration_limit:
            # 1. Choix de la colonne pivot (variable entrante) - CHANGED: argmax instead of argmin
            pivot_col_idx = np.argmax(tableau[-1, :-1])
            
            # 2. Choix de la ligne pivot (variable sortante) via le test du ratio
            ratios = np.full(m_constr, np.inf)
            positive_pivot_col = tableau[:-1, pivot_col_idx] > 1e-6
            
            if not np.any(positive_pivot_col):
                return {"error": "Le problème est non borné. Aucune solution optimale finie."}
            
            # Calcul des ratios uniquement pour les éléments positifs
            ratios[positive_pivot_col] = tableau[:-1, -1][positive_pivot_col] / tableau[:-1, pivot_col_idx][positive_pivot_col]
            pivot_row_idx = np.argmin(ratios)
            
            # NEW: Record pivot information before performing the operation
            pivot_element = tableau[pivot_row_idx, pivot_col_idx]
            
            # Determine variable names for better display
            if pivot_col_idx < n_vars:
                entering_var = f"X{pivot_col_idx + 1}"
            else:
                entering_var = f"S{pivot_col_idx - n_vars + 1}"
                
            leaving_var = f"e{pivot_row_idx + 1}"
            
            pivot_history.append({
                'iteration': iterations + 1,
                'pivot_row': pivot_row_idx,
                'pivot_col': pivot_col_idx,
                'pivot_element': round(pivot_element, 4),
                'entering_var': entering_var,
                'leaving_var': leaving_var,
                'tableau_before': np.copy(tableau).round(4).tolist()  # Store tableau state before pivot
            })
            
            # 3. Pivotage de Gauss-Jordan
            tableau[pivot_row_idx, :] /= pivot_element
            
            for i in range(m_constr + 1):
                if i != pivot_row_idx:
                    multiplier = tableau[i, pivot_col_idx]
                    tableau[i, :] -= multiplier * tableau[pivot_row_idx, :]
            
            iterations += 1

        if iterations >= iteration_limit:
            return {"error": "Limite d'itérations atteinte. Le problème a peut-être cyclé."}

        # Extraction de la solution
        solution = np.zeros(n_vars)
        for j in range(n_vars):
            col = tableau[:-1, j]
            is_basic = (np.count_nonzero(col == 1) == 1) and (np.sum(col) == 1.0)
            if is_basic:
                row_idx = np.where(col == 1.0)[0][0]
                solution[j] = tableau[row_idx, -1]

        return {
            "solution": solution.round(4).tolist(),
            "z_max": round(abs(tableau[-1, -1]), 4),
            "initial_tableau": initial_tableau.round(4).tolist(),
            "final_tableau": tableau.round(4).tolist(),
            "n_vars": n_vars,
            "m_constr": m_constr,
            # NEW: Include pivot history in results
            "pivot_history": pivot_history,
            "total_iterations": iterations
        }
    except Exception as e:
        return {"error": f"Une erreur de calcul est survenue : {e}"}
    finally:
        warnings.resetwarnings()

@app.route("/")
def index():
    """Affiche la page d'accueil."""
    return render_template("index.html")

@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    """Gère l'affichage et le calcul du simplexe."""
    if request.method == "POST":
        try:
            n = int(request.form.get("n", 2))
            m = int(request.form.get("m", 2))

            if "submit_dimensions" in request.form:
                return render_template("index2.html", n=n, m=m, step=2)

            c = [float(request.form[f"c{j}"]) for j in range(n)]
            A = [[float(request.form[f"a{i}{j}"]) for j in range(n)] for i in range(m)]
            b = [float(request.form[f"b{i}"]) for i in range(m)]

            input_data = {'c': c, 'A': A, 'b': b}
            result = simplexe(c, A, b)
            
            return render_template("index2.html", n=n, m=m, step=2, result=result, input_data=input_data)
        
        except (ValueError, KeyError) as e:
            error_message = f"Erreur de saisie. Vérifiez que tous les champs sont remplis avec des nombres valides. (Détail : {e})"
            return render_template("index2.html", n=2, m=2, step=1, error=error_message)

    return render_template("index2.html", n=2, m=2, step=1)

if __name__ == "__main__":
    app.run(debug=True)