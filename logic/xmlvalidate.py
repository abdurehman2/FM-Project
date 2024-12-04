from lxml import etree

def validate_xml(xml_file, xsd_file):
    # Parse the XML and XSD files
    try:
        # Parse the XSD schema
        with open(xsd_file, 'r') as schema_file:
            schema_root = etree.parse(schema_file)
            schema = etree.XMLSchema(schema_root)
        
        # Parse the XML file
        with open(xml_file, 'r') as xml_file:
            xml_root = etree.parse(xml_file)

        # Validate the XML file against the XSD schema
        is_valid = schema.validate(xml_root)
        
        if is_valid:
            print("The XML file is valid according to the schema.")
            return True
        else:
            print("The XML file is NOT valid. Errors:")
            for error in schema.error_log:
                print(error.message)
            return False
    except etree.XMLSyntaxError as e:
        print(f"Error parsing the XML file: {e}")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return
