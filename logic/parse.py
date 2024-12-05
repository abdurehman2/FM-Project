import xml.etree.ElementTree as ET
import xml.etree.ElementTree as ET
import re

def convert_english_to_propositional(english, feature_mapping):
    """
    Convert an English constraint into a propositional logic formula using the feature mapping.
    """
    english = english.strip().lower()

    # Replace feature names in the English statement with their corresponding variable names
    for english_feature, variable_name in feature_mapping.items():
        # Replace only whole words (case insensitive) to avoid partial replacements
        english = re.sub(rf'\b{re.escape(english_feature)}\b', variable_name.lower(), english)

    # Match patterns like "The Location feature is required to filter the catalog by location."
    match = re.match(r"the\s([a-zA-Z\s]+)\sfeature\sis\srequired\s(?:to|for)\sfilter\s([a-zAZ\s]+)", english)
    if match:
        dependent_feature = match.group(1).strip().replace(" ", "")  # Dependent feature (on the left)
        required_feature = match.group(2).strip().replace(" ", "")  # Required feature (on the right)
        
        # Return the implication: required_feature → dependent_feature
        return f"{required_feature} → {dependent_feature}"

    # Match patterns like "Feature A depends on Feature B"
    match = re.match(r"([a-zA-Z\s]+) depends on ([a-zAZ\s]+)", english)
    if match:
        feature_a = match.group(1).strip().replace(" ", "")
        feature_b = match.group(2).strip().replace(" ", "")
        # Return the implication as a propositional logic formula
        return f"{feature_b} → {feature_a}"

    # Match patterns like "Feature A cannot be used without Feature B"
    match = re.match(r"([a-zA-Z\s]+) cannot be used without ([a-zAZ\s]+)", english)
    if match:
        feature_a = match.group(1).strip().replace(" ", "")
        feature_b = match.group(2).strip().replace(" ", "")
        # Return the implication as a propositional logic formula
        return f"{feature_b} → {feature_a}"

    # Handle generic "must be selected before" case
    match = re.match(r"([a-zA-Z\s]+) must be selected before ([a-zAZ\s]+)", english)
    if match:
        feature_a = match.group(1).strip().replace(" ", "")
        feature_b = match.group(2).strip().replace(" ", "")
        # Return the implication as a propositional logic formula
        return f"{feature_a} → {feature_b}"

    # If no match found, return None to indicate unsupported format
    return None


def parse_feature_model(file_path):
    """
    Parse the XML feature model and generate propositional logic formulas.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    formulas = []
    feature_mapping = {}

    def parse_feature(feature, parent=None):
        name = feature.attrib.get("name")
        mandatory = feature.attrib.get("mandatory", "false") == "true"

        # Add to feature mapping: English name -> Variable name
        variable_name = name.replace(" ", "")  # Variable name is the feature name without spaces
        feature_mapping[name.lower()] = variable_name.lower()  # Map English name to variable name

        # Generate logic for mandatory features
        if parent and mandatory:
            formulas.append(f"{parent} → {variable_name}")

        # Add child-to-parent relationship
        if parent:
            formulas.append(f"{variable_name} → {parent}")

        # Parse child features
        for child in feature.findall("feature"):
            parse_feature(child, name)

        # Parse groups
        group = feature.find("group")
        if group is not None:
            group_type = group.attrib.get("type")
            child_names = [child.attrib.get("name") for child in group.findall("feature")]

            if group_type == "xor":
                # XOR: Exactly one child can be selected
                xor_logic = " ∨ ".join(child_names)
                pairwise_exclusions = " ∧ ".join(
                    [f"~({a} ∧ {b})" for i, a in enumerate(child_names) for b in child_names[i + 1:]]
                )
                formulas.append(f"{name} → ({xor_logic})")
                formulas.append(f"{name} → ({pairwise_exclusions})")

                # Add child-to-parent relationships for XOR
                for child in child_names:
                    formulas.append(f"{child} → {name}")
            elif group_type == "or":
                # OR: At least one child must be selected
                or_logic = " ∨ ".join(child_names)
                formulas.append(f"{name} → ({or_logic})")

                # Add child-to-parent relationships for OR
                for child in child_names:
                    formulas.append(f"{child} → {name}")

    # def parse_constraints(constraints):
    #     for constraint in constraints.findall("constraint"):
    #         english = constraint.find("englishStatement")
    #         boolean_expression = constraint.find("booleanExpression")

    #         if boolean_expression is not None and boolean_expression.text:
    #             formulas.append(boolean_expression.text)
    #         elif english is not None and english.text:
    #             # Convert English constraints into Propositional Logic using the feature mapping
    #             english_constraint = english.text.strip()
                
    #             # Pre-process English statement by replacing feature names with variable names from the XML mapping
    #             for english_feature, variable_name in feature_mapping.items():
    #                 english_constraint = re.sub(rf'\b{re.escape(english_feature)}\b', variable_name.lower(), english_constraint)
                
    #             propositional_constraint = convert_english_to_propositional(english_constraint, feature_mapping)
    #             if propositional_constraint:
    #                 formulas.append(propositional_constraint)
    #             else:
    #                 print(f"Skipping unsupported English constraint: {english_constraint}")

    # Start parsing from the root
    root_feature = root.find("feature")
    if root_feature is not None:
        root_name = root_feature.attrib.get("name")
        formulas.append(f"{root_name} = True")  # Root feature is always true
        parse_feature(root_feature)

    # # Parse constraints
    # constraints = root.find("constraints")
    # if constraints is not None:
    #     parse_constraints(constraints)

    return formulas



import itertools

def parse_feature_model1(file_path):
    """
    Parse the XML feature model and extract features, groups, and their relationships.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    features = {}
    # Start parsing the root feature
    def parse_feature(feature, parent=None):
        name = feature.attrib.get("name")
        mandatory = feature.attrib.get("mandatory", "false") == "true"

        # Initialize feature in the dictionary if not already present
        if name not in features:
            features[name] = {'mandatory': mandatory, 'parents': [], 'children': [], 'group': None}

        # Add the current feature as a child to its parent
        if parent:
            features[parent]['children'].append(name)
            features[name]['parents'].append(parent)

        # Parse child features
        for child in feature.findall("feature"):
            parse_feature(child, name)

        # Parse groups (xor, or)
        group = feature.find("group")
        if group is not None:
            group_type = group.attrib.get("type")
            features[name]['group'] = group_type

            child_names = [child.attrib.get("name") for child in group.findall("feature")]
            for child_name in child_names:
                # Add group relationships (parent-child)
                if child_name not in features:
                    features[child_name] = {'mandatory': False, 'parents': [], 'children': [], 'group': None}
                features[name]['children'].append(child_name)
                features[child_name]['parents'].append(name)

    # Parse root feature
    root_feature = root.find("feature")
    if root_feature is not None:
        parse_feature(root_feature)

    return features

import itertools

def find_minimum_working_product(features):
    """
    Find the Minimum Working Product (MWP) from the parsed features, creating sets for xor configurations.
    """
    mwp_set = set()
    mandatory_features = [feature for feature, details in features.items() if details['mandatory']]

    # Add root node (it will always be in the MWP)
    root_node = next((feature for feature, details in features.items() if details['parents'] == []), None)
    if root_node:
        mwp_set.add(root_node)

    # Add all mandatory features to the MWP
    for feature in mandatory_features:
        mwp_set.add(feature)

    xor_sets = []
    or_sets = []

    # Iterate through the features
    for feature in mandatory_features:
        group_type = features[feature].get('group')

        if group_type == 'xor':
            # If feature is in an xor group, we need to ensure exactly one is selected from its group
            group_features = features[feature]['children']
            xor_combinations = []

            # Generate all possible combinations of features where exactly one is selected
            for combination in itertools.combinations(group_features, 1):
                xor_combinations.append(set(combination))
            
            xor_sets.append(xor_combinations)

        elif group_type == 'or':
            # For 'or' group, at least one feature must be included, but only one feature is allowed in the MWP
            group_features = features[feature]['children']
            # Select only one feature from the OR group for MWP
            or_sets.append([set([feature]) for feature in group_features])

    # Now, we need to combine the mandatory features with xor and or sets
    all_configurations = []
    # Start by adding the mandatory features to each possible combination of xor and or configurations
    for xor_combination in itertools.product(*xor_sets):
        for or_combination in itertools.product(*or_sets):
            mwp_configuration = set(mwp_set)  # Start with mandatory features

            # Add xor group configuration
            for combination in xor_combination:
                mwp_configuration.update(combination)

            # Add or group configuration, ensuring that only one child is added for 'or'
            for combination in or_combination:
                mwp_configuration.update(combination)

            # Convert the set to a sorted list for a more readable output
            all_configurations.append(sorted(mwp_configuration))

    return all_configurations



# feature_model_parser.py

import xml.etree.ElementTree as ET

def parse_feature_model2(file_path):
    """
    Parse the XML feature model and extract features, groups, and their relationships.
    Features are parsed with additional logic for mandatory/optional constraints, parent-child relationships, 
    group types (XOR/OR), and dynamic constraint validation.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    features = {}

    def parse_feature(feature, parent=None):
        """
        Recursively parse each feature in the feature model XML.
        This function supports:
        - Parsing mandatory/optional features
        - Parent-child relationships
        - Group types (XOR/OR) with proper constraints
        """
        name = feature.attrib.get("name")
        mandatory = feature.attrib.get("mandatory", "false") == "true"

        # Initialize the feature in the dictionary if it hasn't been initialized
        if name not in features:
            features[name] = {
                'mandatory': mandatory,
                'parents': [],
                'children': [],
                'group': None,
                'group_type': None,
                'is_selected': False  # Tracks whether the feature is selected
            }

        # If the feature has a parent, add the parent-child relationship
        if parent:
            features[parent]['children'].append(name)
            features[name]['parents'].append(parent)

        # Parse child features
        for child in feature.findall("feature"):
            parse_feature(child, name)

        # Parse groups (XOR/OR)
        group = feature.find("group")
        if group is not None:
            group_type = group.attrib.get("type")  # 'xor' or 'or'
            features[name]['group'] = group
            features[name]['group_type'] = group_type

            child_names = [child.attrib.get("name") for child in group.findall("feature")]
            for child_name in child_names:
                # Add group relationships (parent-child)
                if child_name not in features:
                    features[child_name] = {'mandatory': False, 'parents': [], 'children': [], 'group': None, 'group_type': None, 'is_selected': False}
                features[name]['children'].append(child_name)
                features[child_name]['parents'].append(name)

    # Start parsing the root feature
    root_feature = root.find("feature")
    if root_feature is not None:
        parse_feature(root_feature)

    # Helper function to validate feature selection based on constraints
    def validate_feature_selection(feature_name, is_selected):
        """
        Validates the feature selection based on mandatory/optional constraints.
        If a mandatory feature is deselected, all dependent features must also be deselected.
        If a feature in an XOR group is selected, other features in the group must be deselected.
        """
        feature = features[feature_name]
        feature['is_selected'] = is_selected

        # Handle mandatory constraint - if deselected, deselect dependent features
        if feature['mandatory'] and not is_selected:
            for child in feature['children']:
                validate_feature_selection(child, False)
            for parent in feature['parents']:
                validate_feature_selection(parent, False)

        # Handle XOR group constraint - if selected, deselect other features in the same group
        if feature['group_type'] == 'xor' and is_selected:
            for sibling in feature['children']:
                if sibling != feature_name:  # Don't deselect the selected feature
                    validate_feature_selection(sibling, False)

        # Handle OR group constraint - no deselection logic required for OR
        if feature['group_type'] == 'or' and is_selected:
            for sibling in feature['children']:
                validate_feature_selection(sibling, True)

    # Function to visualize the feature model (convert to a suitable structure for rendering)
    def visualize_feature_model(features):
        """
        Visualizes the feature model based on the parsed data.
        Converts the features dictionary into a tree-like structure for rendering on the frontend.
        """
        # A simple representation, you can extend this to a more complex visualization
        return {
            "features": list(features.keys()),  # List of feature names
            "relationships": [(f, features[f]['children']) for f in features]  # Parent-child relationships
        }

    # Return parsed features and the validation function
    return features, validate_feature_selection, visualize_feature_model

