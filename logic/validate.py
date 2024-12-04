from pysat.solvers import Solver

def validate_configuration(cnf, feature_ids, selected_features, feature_hierarchy):
    from pysat.solvers import Solver
    
    solver = Solver()
    for clause in cnf.clauses:
        solver.add_clause(clause)

    selected_ids = [feature_ids[feature] for feature in selected_features if feature in feature_ids]
    assumptions = selected_ids  # Assuming selected features are true

    if solver.solve(assumptions=assumptions):
        model = solver.get_model()

        # Ensure model includes parent-child relationships
        id_to_feature = {v: k for k, v in feature_ids.items()}
        model_features = {id_to_feature[abs(var)]: (var > 0) for var in model if abs(var) in id_to_feature}

        for feature in selected_features:
            # Check parent-child consistency
            parent = feature_hierarchy[feature].get('parent')
            if parent and model_features[feature]:  # If a feature is selected
                if not model_features[parent]:  # Its parent must also be selected
                    return False, []

        return True, model
    else:
        return False, []


