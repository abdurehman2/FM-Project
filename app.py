import os
from lxml import etree
import traceback
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, jsonify
from logic.parse import parse_feature_model1, find_minimum_working_product, parse_feature_model
from logic.xmlvalidate import validate_xml

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xml'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
xsd_schema = 'logic/feature-model.xsd'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse', methods=['POST'])
def parse_xml():
    if 'xml' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['xml']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)
        try:
            if xsd_schema:
                with open(xsd_schema, 'rb') as xsd_file:
                    schema_doc = etree.parse(xsd_file)
                    schema = etree.XMLSchema(schema_doc)
                xml_doc = etree.parse(filepath)
                schema.assertValid(xml_doc)
            tree = etree.parse(filepath)
            root = tree.getroot()
            features = root.xpath('//feature/@name')
            constraints = [
                {"englishStatement": constraint.findtext('englishStatement')}
                for constraint in root.xpath('//constraints/constraint')
                if constraint.findtext('englishStatement')
            ]
            if not constraints:
                return jsonify({"error": "No cross-tree constraints found in the XML."}), 400
            return jsonify({"features": features, "constraints": constraints})
        except Exception as e:
            return jsonify({"error": f"Error parsing file: {str(e)}"}), 500
    return jsonify({"error": "Invalid file type. Only XML files are allowed."}), 400

@app.route('/process_logic_and_mwp', methods=['POST'])
def process_logic_and_mwp():
    try:
        data = request.json
        logic_data = data.get("logicData", [])

        # Validate logic data format
        for logic in logic_data:
            if not isinstance(logic, dict) or 'constraintIndex' not in logic or 'logic' not in logic:
                return jsonify({"error": "Invalid logic format"}), 400

        logic_mapping = {f"constraint-{logic['constraintIndex']}": logic['logic'] for logic in logic_data}
        print("Propositional Logic Received:", logic_mapping)

        # Ensure XML file exists
        xml_file = 'uploads/feature-model.xml'
        if not os.path.exists(xml_file):
            return jsonify({"error": "XML file not found"}), 400

        # Validate XML file
        valid = validate_xml(xml_file, xsd_schema)
        if not valid:
            return jsonify({"error": "Invalid XML file"}), 400

        # Parse the feature model and generate logic
        propositional_logic = parse_feature_model(xml_file)

        # Parse features for MWP calculation
        features = parse_feature_model1(xml_file)

        # Calculate MWP configurations
        mwp_configurations = find_minimum_working_product(features)
        print("MWP Configurations:", mwp_configurations)

        # Format the MWP configurations for output
        mwp_list = [", ".join(config) for config in mwp_configurations]

        # Return MWP, the entered logic, and propositional logic
        response = {
            "logicMapping": logic_mapping,
            "mwpConfigurations": mwp_list,
            "propositionalLogic": propositional_logic,  # Add this to the response
        }
        return jsonify(response)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Error processing logic and MWP: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
