from parse import parse_feature_model, parse_features
from validate import validate_configuration
from translate import translate_to_cnf
from xmlvalidate import validate_xml
from calculate import calculate_mwp

xml_file = 'feature-model.xml'

valid = validate_xml(xml_file, 'feature-model.xsd')

# Step 1: Parse XML
logic_formulas, feature_ids = parse_feature_model(xml_file)

# Display propositional logic as feature names
print("Propositional Logic Representation:")
for formula in logic_formulas:
    if formula.startswith("#"):  # Print constraints as comments
        print(formula)
    else:
        # Replace IDs with feature names
        id_to_feature = {v: k for k, v in feature_ids.items()}
        formula_with_names = formula
        for feature_id, feature_name in id_to_feature.items():
            formula_with_names = formula_with_names.replace(str(feature_id), feature_name)
        print(formula_with_names)

features, constraints = parse_features(xml_file)

# Step 2: Translate to CNF
cnf, feature_ids = translate_to_cnf(features, constraints)

# Step 3: Calculate MWP
mwp_features = calculate_mwp(features, feature_ids, cnf)
print("\nMinimum Working Product (MWP) Configuration:")
print("MWP Features:", mwp_features)
