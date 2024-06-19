import lxml.etree as ET
import svgwrite

# Parse all model classes
def parse_model_classes(elem):
    m_classes_raw = elem.findall('.//Class')

    # Remove all nested and not needed classes
    to_remove = []

    for m_class_raw in m_classes_raw:
        if m_class_raw.getparent().getparent().tag != 'Model' and m_class_raw.getparent().getparent().tag != 'Package':
            to_remove.append(m_class_raw)

    for m_class_raw in to_remove:
        m_classes_raw.remove(m_class_raw)
    # End of removal

    # Change all classes to needed format
    classes_return = {}

    for m_class_raw in m_classes_raw:
        name = m_class_raw.get('Name')
        attributes = []
        operations = []
        # Get all attributes
        for child in m_class_raw.findall('.//Attribute'):
            attributes.append({'Name': child.attrib['Name'], 'Visibility': child.attrib['Visibility'], 'type': get_type(child), 'modifier': child.attrib['TypeModifier']})
        # Get all operations
        for child in m_class_raw.findall('.//Operation'):
            params = []
            # Get all parameters in operation
            for param in child.findall('.//Parameter'):
                params.append({'Name': param.get('Name'), 'type': get_type(param), 'modifier': child.attrib['TypeModifier']})
            operations.append({'Name': child.attrib['Name'], 'Visibility': child.attrib['Visibility'], 'Parameters': params, 'return_type': get_return_type(child), 'modifier': child.attrib['TypeModifier']})

        # We assume, that class supposed to have at least 1 attribute or 1 operation, if not, it's not a class (for us)
        if len(attributes) > 0 or len(operations) > 0:
            classes_return[m_class_raw.get('Id')] = {'Name': name, 'Attributes': attributes, 'Operations': operations}

    return classes_return


# Parse all diagram classes (visual ones)
def parse_diagram_classes(elem):
    m_classes_raw = elem.findall('.//Class')

    classes_return = {}

    for m_class_raw in m_classes_raw:
        x = m_class_raw.get('X')
        y = m_class_raw.get('Y')
        width = m_class_raw.get('Width')
        height = m_class_raw.get('Height')
        id = m_class_raw.get('Id')
        master = m_class_raw.get('Model')  # ID of model class
        color = rgb_to_hex(m_class_raw.find('.//FillColor').get('Color'))
        font_shift = parse_font_shift(m_class_raw)
        classes_return[master] = {'x': x, 'y': y, 'width': width, 'height': height, 'color': color, 'id': id, 'shift': font_shift}

    return classes_return


# Get type of attribute, operation or something else
def get_type(elem):
    type = elem.find('.//Type')
    to_return = None
    if type is not None:
        datatype = type.find('.//DataType')
        internal_class = type.find('.//Class')

        if internal_class is not None:
            to_return = internal_class.get('Name')
        elif datatype is not None:
            to_return = datatype.get('Name')
    else:
        to_return = elem.get('Type', None)
    return to_return


# Get return type of operation
def get_return_type(elem):
    type = elem.find('.//ReturnType')
    to_return = None
    if type is not None:
        datatype = type.find('.//DataType')
        internal_class = type.find('.//Class')

        if internal_class is not None:
            to_return = internal_class.get('Name')
        elif datatype is not None:
            to_return = datatype.get('Name')
    else:
        to_return = elem.get('ReturnType', None)
    return to_return


# Parse line points
def parse_points(elem):
    points_raw = elem.findall('.//Points')
    points = []

    for points_obj in points_raw:
        point_points = []

        id = points_obj.getparent().get('Id')

        for child in points_obj.iterchildren():
            x = child.attrib.get('X')
            y = child.attrib.get('Y')
            point_points.append({'x': x, 'y': y})
        points.append({'points': point_points, 'id': id})
    return points


# Parse font shift (font height originally)
def parse_font_shift(elem):
    shift = 0
    for child in elem:
        if child.tag.endswith('ElementFont'):
            shift += int(child.attrib.get('Size'))
    return shift


# Change RGB (rgb(x, y, z)) to HEX (#FFFFFF)
def rgb_to_hex(rgb_string):
    # Remove the "rgb(" and ")" part and split the remaining string by commas
    rgb_values = rgb_string[4:-1].split(',')

    # Convert each component to an integer
    r, g, b = [int(value) for value in rgb_values]

    # Format the integers as hexadecimal and return the combined string
    return f'#{r:02X}{g:02X}{b:02X}'


# Main parse and draw function
def parse(xml_file, output_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # SVG setup
    dwg = svgwrite.Drawing(output_file, profile='full', size=('2000px', '1600px'))

    # Define arrow marker for lines
    arrow_marker = dwg.marker(id='arrow', insert=(10, 5), size=(10, 10), orient='auto')
    arrow_marker.add(dwg.path(d='M0,0 L0,10 L10,5 Z', fill='black'))

    dot_marker = dwg.marker(insert=(5, 5), size=(10, 10), orient='auto')
    dot_marker.add(dwg.circle(center=(5, 5), r=3, fill='black'))
    dwg.defs.add(dot_marker)
    dwg.defs.add(arrow_marker)

    x_arrow_marker = dwg.marker(insert=(0, 10), size=(20, 20), orient='auto')
    x_arrow_marker.add(dwg.line(start=(5, 0), end=(15, 20), stroke='black', stroke_width=1))
    x_arrow_marker.add(dwg.line(start=(5, 20), end=(15, 0), stroke='black', stroke_width=1))
    dwg.defs.add(x_arrow_marker)

    # Extracting classes and points
    model_classes = parse_model_classes(root.find('.//Models'))
    diagram_classes = parse_diagram_classes(root.find('.//Diagrams'))
    points = parse_points(root)

    combined_classes = {}

    # Combining of model and diagram classes
    for model_class_id, model_class in model_classes.items():
        id = model_class_id
        name = model_class.get('Name')
        attributes = model_class.get('Attributes')
        operations = model_class.get('Operations')
        x = diagram_classes[id]['x']
        y = diagram_classes[id]['y']
        width = diagram_classes[id]['width']
        height = diagram_classes[id]['height']
        color = diagram_classes[id]['color']
        shift = diagram_classes[id]['shift']
        combined_classes[id] = {'id': id, 'name': name, 'attributes': attributes, 'operations': operations, 'x': x, 'y': y, 'width': width, 'height': height, 'color': color, 'shift': shift}

    # Draw classes
    for class_id, class_info in combined_classes.items():
        name = class_info.get('name')
        attributes = class_info.get('attributes')
        operations = class_info.get('operations')
        x = int(class_info['x'])
        y = int(class_info['y'])
        width = int(class_info['width'])
        height = int(class_info['height'])
        color = class_info['color']
        shift = int(class_info['shift'])

        # Draw box of class
        dwg.add(dwg.rect(insert=(x, y), size=(width, height), fill=color, stroke='black'))

        # Add name to box
        dwg.add(
            dwg.text(name, insert=(x + width / 2, y + shift),
                     text_anchor='middle', font_size='11px',
                     font_family='Arial'))

        # Add separator between name and the rest
        dwg.add(dwg.line(start=(x, y + shift + 2), end=(x + width, y + shift + 2),
                         stroke='black'))

        # Cursor that shows where to write
        write_at = y + shift * 2 + 1.3

        # List all attributes of class
        for attribute in attributes:
            visibility = ''
            type = ''
            if attribute.get('Visibility') == 'private':
                visibility = '-'
            elif attribute.get('Visibility') == 'public':
                visibility = '+'
            elif attribute.get('Visibility') == 'package':
                visibility = '~'
            elif attribute.get('Visibility') == 'protected':
                visibility = '#'

            if attribute.get('type') is not None:
                type = f": {attribute.get('type')}"

            # Writes attribute like "+ Name: int"
            dwg.add(dwg.text(f"{visibility} {attribute.get('Name')}{type}", insert=(x + 2, write_at), text_anchor='start',
                                 font_size='10px',
                                 font_family='Arial'))
            write_at += shift

        # If cursor moved and class has operations, draw separator
        if write_at != y + shift * 2 + 1.3 and len(operations) > 0:
            dwg.add(dwg.line(start=(x, write_at - shift+2), end=(x + width, write_at - shift+2),
                         stroke='black'))
            write_at += 1

        # List all operations
        for operation in operations:
            visibility = ''
            return_type = ''
            parameters = ''
            modifier = operation.get('modifier')
            if operation.get('Visibility') == 'private':
                visibility = '-'
            elif operation.get('Visibility') == 'public':
                visibility = '+'
            elif operation.get('Visibility') == 'package':
                visibility = '~'
            elif operation.get('Visibility') == 'protected':
                visibility = '#'

            if operation.get('return_type') is not None:
                return_type = f": {operation.get('return_type')}"

            # Get string of all parameters of this operation
            if len(operation.get('Parameters')) > 0:
                parameters_objs = operation.get('Parameters')
                for i in range(len(parameters_objs)):
                    parameter_type = f': {parameters_objs[i].get("type")}' if parameters_objs[i].get("type") is not None else ''
                    parameters += f'{parameters_objs[i].get("Name")}{parameter_type}{parameters_objs[i].get("modifier")}'
                    if i < len(parameters_objs) - 1:
                        parameters += ', '

            # Write operation like "+ Name(smt: int): void"
            dwg.add(dwg.text(f"{visibility}{operation.get('Name')}({parameters}){return_type}{modifier}", insert=(x + 2, write_at), text_anchor='start',
                             font_size='10px',
                             font_family='Arial'))
            write_at += shift

        # Draw all connections of classes
        previous = None
        for x in range(len(points)):
            actual_points = points[x].get('points')
            for i in range(len(actual_points)):
                if previous is None:
                    previous = actual_points[i]
                    continue

                actual_point = actual_points[i]

                # If it first connection, draw line with 'x'
                if i == 1:
                    dwg.add(dwg.line(start=(previous.get('x'), previous.get('y')),
                                     end=(actual_point.get('x'), actual_point.get('y')), stroke='black',
                                     marker_start=x_arrow_marker.get_funciri())),

                # If it last connection, draw 2 lines on top of each other. One with arrow, one with black dot
                if i == len(actual_points) - 1:
                    dwg.add(dwg.line(start=(previous.get('x'), previous.get('y')),
                                     end=(actual_point.get('x'), actual_point.get('y')), stroke='black',
                                     marker_end=arrow_marker.get_funciri()))
                    dwg.add(dwg.line(start=(previous.get('x'), previous.get('y')),
                                     end=(actual_point.get('x'), actual_point.get('y')), stroke='black',
                                     marker_end=dot_marker.get_funciri()))
                    break

                # If it's line between first and last, draw line with nothing
                dwg.add(
                    dwg.line(start=(previous.get('x'), previous.get('y')), end=(actual_point.get('x'), actual_point.get('y')),
                             stroke='black'))

                previous = actual_point
            previous = None

    # Save the SVG file
    dwg.save()
    print('SVG file ' + output_file + ' created successfully.')


def main():
    xml_file = 'sumxmls/simple_class_huge.xml'
    output_file = 'class_diagram.svg'

    parse(xml_file, output_file)


if __name__ == "__main__":
    main()
