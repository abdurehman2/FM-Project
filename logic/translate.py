from pysat.formula import CNF

def translate_to_cnf(feature_hierarchy, constraints):
    cnf = CNF()
    feature_ids = {name: i + 1 for i, name in enumerate(feature_hierarchy)}  # Map features to unique IDs

    # Encode mandatory relationships
    for feature, details in feature_hierarchy.items():
        if details['parent']:
            parent_id = feature_ids[details['parent']]
            child_id = feature_ids[feature]
            # Parent implies child (mandatory relationship)
            if details['mandatory']:
                cnf.append([-parent_id, child_id])  # parent → child
            # Child implies parent
            cnf.append([-child_id, parent_id])  # child → parent

    # Encode XOR and OR groups
    for feature, details in feature_hierarchy.items():
        if details.get('group'):
            group_type = details['group']['type']
            children = [feature_ids[child] for child in details['group']['children']]

            if group_type == 'xor':  # XOR: (A ∧ ¬B) ∨ (B ∧ ¬A) ...
                for i, a in enumerate(children):
                    for b in children[i + 1:]:
                        cnf.append([-a, -b])  # At most one selected
                cnf.append(children)  # At least one selected

            elif group_type == 'or':  # OR: At least one selected
                cnf.append(children)

    # Translate cross-tree constraints
    for constraint in constraints:
        if "requires" in constraint.lower():
            # Example: "The Location feature is required to filter the catalog by location."
            parts = constraint.split("requires")
            req_feature = feature_ids[parts[0].strip()]
            dependent_feature = feature_ids[parts[1].strip()]
            cnf.append([-dependent_feature, req_feature])  # dependent → required

    return cnf, feature_ids
