from flask import Flask, render_template, request
from scipy.optimize import linprog
import re

app = Flask(__name__)

# --- Fonction d'Analyse et de Résolution ---
def solve_simplex_from_text(text_input):
    """
    Analyse le texte pour extraire les données et résoudre le Simplex.
    ⚠️ NOTE : Cette analyse est TRÈS simplifiée. Elle s'attend à un format
    très spécifique (ex: max 3x + 4y | 1x + 1y <= 10 | 2x + 1y <= 15).
    """
    
    # Séparer la fonction objectif des contraintes
    try:
        parts = [p.strip() for p in text_input.split('|')]
        if len(parts) < 2:
            raise ValueError("Le format d'entrée est incorrect. Utilisez '|' pour séparer l'objectif et les contraintes.")
            
        objectif_str = parts[0].lower()
        contraintes_str = parts[1:]
    except Exception:
        raise ValueError("Erreur de formatage initial. Assurez-vous d'avoir au moins une fonction objectif et une contrainte.")


    # --- 1. Extraction de la Fonction Objectif (c) ---
    if 'max' in objectif_str:
        is_max = True
    elif 'min' in objectif_str:
        is_max = False
    else:
        raise ValueError("L'objectif doit commencer par 'max' ou 'min'.")

    # Extraire les coefficients (ici, on suppose deux variables x et y)
    coefficients_match = re.findall(r'(\d+)\s*[xy]', objectif_str)
    if len(coefficients_match) != 2:
        raise ValueError("Veuillez spécifier l'objectif avec deux variables (x et y) et leurs coefficients.")

    c = [float(coeff) for coeff in coefficients_match]
    
    # Inverser les signes pour la maximisation (linprog minimise par défaut)
    if is_max:
        c = [-val for val in c]


    # --- 2. Extraction des Contraintes (A_ub et b_ub) ---
    A_ub = []
    b_ub = []

    for constraint_str in contraintes_str:
        # On suppose que toutes les contraintes sont de type '<='
        match = re.match(r'(\d+)x\s*\+\s*(\d+)y\s*<=\s*(\d+)', constraint_str.strip())
        
        if not match:
            raise ValueError(f"Contrainte non reconnue ou formatée incorrectement: '{constraint_str}'. Format attendu: 'Ax + By <= C'")
            
        # [A, B]
        A_ub.append([float(match.group(1)), float(match.group(2))])
        # [C]
        b_ub.append(float(match.group(3)))

    
    # --- 3. Résolution ---
    try:
        # La méthode 'highs' est souvent plus rapide
        res = linprog(c, A_ub=A_ub, b_ub=b_ub, method='highs', bounds=(0, None)) 
    except Exception as e:
        raise Exception(f"Erreur lors de l'exécution du solveur SciPy: {e}")

    # --- 4. Formatage du Résultat ---
    if res.success:
        optimal_value = -res.fun if is_max else res.fun
        
        resultat = {
            "statut": "Optimal",
            "valeur_optimale": round(optimal_value, 2),
            "variables": {"x": round(res.x[0], 2), "y": round(res.x[1], 2)},
            "message": "Solution trouvée avec succès."
        }
    else:
        resultat = {"statut": "Échec", "message": f"Impossible de trouver la solution : {res.message}"}

    return resultat


@app.route('/', methods=['GET', 'POST'])
def simplex_interface():
    resultat = None
    input_text = ""
    
    if request.method == 'POST':
        input_text = request.form.get('simplex_problem', '')
        
        if input_text:
            try:
                # Appeler la fonction d'analyse et de résolution
                resultat = solve_simplex_from_text(input_text)
            except (ValueError, Exception) as e:
                # Capturer les erreurs d'analyse ou de solveur
                resultat = {"statut": "Erreur", "message": str(e)}

    # Renvoyer la page avec le résultat ou le formulaire vide
    return render_template('ai.html', resultat=resultat, input_text=input_text)

if __name__ == '__main__':
    app.run(debug=True)