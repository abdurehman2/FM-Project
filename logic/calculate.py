def calculate_mwp(features, feature_ids, cnf):
    from pysat.solvers import Solver
    
    solver = Solver()
    for clause in cnf.clauses:
        solver.add_clause(clause)

    selected_ids = set()
    id_to_feature = {v: k for k, v in feature_ids.items()}
    mwp_features = []

    # Try enabling features one by one to find the minimal working configuration
    for feature, feature_id in feature_ids.items():
        if feature_id not in selected_ids:
            if solver.solve(assumptions=list(selected_ids) + [feature_id]):
                selected_ids.add(feature_id)
                mwp_features.append(feature)

    return mwp_features