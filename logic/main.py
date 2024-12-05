from parse import parse_feature_model, find_minimum_working_product, parse_feature_model1
from validate import validate_configuration
from translate import translate_to_cnf
from xmlvalidate import validate_xml
from calculate import calculate_mwp




xml_file = 'feature-model.xml'

valid = validate_xml(xml_file, 'feature-model.xsd')

# Step 1: Parse XML
#logic_formulas, feature_ids = parse_feature_model(xml_file)
logic_formulas = parse_feature_model(xml_file)
for formula in logic_formulas:
        print(formula)

features = parse_feature_model1(xml_file)

    # Find the Minimum Working Product (MWP) configurations that satisfy crosstree constraints
mwp_configurations = find_minimum_working_product(features)

    # Output the MWP configurations
print("Minimum Working Product (MWP) configurations satisfying crosstree constraints:")
for config in mwp_configurations:
    print(", ".join(config))
# # Display propositional logic as feature names
# print("Propositional Logic Representation:")
# for formula in logic_formulas:
#     if formula.startswith("#"):  # Print constraints as comments
#         print(formula)
#     else:
#         # Replace IDs with feature names
#         id_to_feature = {v: k for k, v in feature_ids.items()}
#         formula_with_names = formula
#         for feature_id, feature_name in id_to_feature.items():
#             formula_with_names = formula_with_names.replace(str(feature_id), feature_name)
#         print(formula_with_names)

s
