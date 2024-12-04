import xml.etree.ElementTree as ET

def parse_feature_model(xml_file):
    """
    Parses the feature model XML file and translates it into propositional logic formulas.
    
    :param xml_file: Path to the feature model XML file.
    :return: A tuple containing the logical formulas and the mapping of feature names.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    logic_formulas = []
    feature_mapping = {}

    def translate_features(feature_element, parent=None):
        """
        Recursively parses features and translates them to propositional logic.

        :param feature_element: The current XML feature element being processed.
        :param parent: The parent feature of the current feature.
        """
        feature_name = feature_element.get('name')
        mandatory = feature_element.get('mandatory', 'false').lower() == 'true'

        # Add feature to mapping (use numbers for simpler translation)
        if feature_name not in feature_mapping:
            feature_mapping[feature_name] = len(feature_mapping) + 1
        feature_id = feature_mapping[feature_name]

        if parent:
            parent_id = feature_mapping[parent]

            # Mandatory feature: Parent -> Child
            if mandatory:
                logic_formulas.append(f"{parent_id} -> {feature_id}")

            # Optional feature: Parent -> (Parent <-> Child)
            else:
                logic_formulas.append(f"{parent_id} -> ({feature_id} | ~{feature_id})")

        # Handle groups (xor, or)
        group = feature_element.find('group')
        if group is not None:
            group_type = group.get('type')
            children = [child.get('name') for child in group.findall('feature')]

            # Add children to mapping
            child_ids = []
            for child in children:
                if child not in feature_mapping:
                    feature_mapping[child] = len(feature_mapping) + 1
                child_ids.append(feature_mapping[child])

            # XOR: Only one child can be selected
            if group_type == "xor":
                logic_formulas.append(" & ".join([
                    f"~({child_ids[i]} & {child_ids[j]})"
                    for i in range(len(child_ids))
                    for j in range(i + 1, len(child_ids))
                ]))
                logic_formulas.append(f"{feature_id} -> ({' | '.join(map(str, child_ids))})")

            # OR: At least one child must be selected
            elif group_type == "or":
                logic_formulas.append(f"{feature_id} -> ({' | '.join(map(str, child_ids))})")

        # Recurse through child features
        for child in feature_element.findall('feature'):
            translate_features(child, feature_name)

    # Parse the root feature and its hierarchy
    root_feature = root.find('feature')
    if root_feature is not None:
        translate_features(root_feature)

    # Parse and translate constraints
    constraints_element = root.find('constraints')
    if constraints_element is not None:
        for constraint in constraints_element.findall('constraint'):
            english_statement = constraint.find('englishStatement').text
            if english_statement:
                # For now, just append as a comment
                logic_formulas.append(f"# {english_statement}")

    return logic_formulas, feature_mapping

import xml.etree.ElementTree as ET

def parse_features(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    feature_hierarchy = {}
    constraints = []

    def parse_features(feature_element, parent=None):
        feature_name = feature_element.get('name')
        mandatory = feature_element.get('mandatory', 'false') == 'true'
        feature_hierarchy[feature_name] = {
            'parent': parent,
            'mandatory': mandatory,
            'group': None,
            'children': []
        }

        # Handle groups (xor, or)
        group = feature_element.find('group')
        if group is not None:
            group_type = group.get('type')
            children = [child.get('name') for child in group.findall('feature')]
            feature_hierarchy[feature_name]['group'] = {
                'type': group_type,
                'children': children
            }
            for child in children:
                feature_hierarchy[child] = {'parent': feature_name, 'mandatory': False}

        # Recurse through children
        for child in feature_element.findall('feature'):
            parse_features(child, feature_name)

    # Parse the root feature and its hierarchy
    root_feature = root.find('feature')
    parse_features(root_feature)

    # Parse constraints
    for constraint in root.find('constraints').findall('constraint'):
        english_statement = constraint.find('englishStatement').text
        constraints.append(english_statement)

    return feature_hierarchy, constraints