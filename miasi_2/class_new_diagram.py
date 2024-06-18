import lxml.etree as ET
import svgwrite


def parse_model_classes(elem):
    m_classes_raw = elem.findall('.//Class')

    to_remove = []

    for m_class_raw in m_classes_raw:
        if m_class_raw.getparent().getparent().tag != 'Model' and m_class_raw.getparent().getparent().tag != 'Package':
            to_remove.append(m_class_raw)

    for m_class_raw in to_remove:
        m_classes_raw.remove(m_class_raw)

    classes_return = {}

    for m_class_raw in m_classes_raw:
        name = m_class_raw.get('Name')
        attributes = []
        operations = []
        for child in m_class_raw.findall('.//Attribute'):
            attributes.append({'Name': child.attrib['Name'], 'Visibility': child.attrib['Visibility']})
        for child in m_class_raw.findall('.//Operation'):
            params = []
            for param in child.findall('.//Parameter'):
                params.append({'Name': param.get('Name')})
            operations.append({'Name': child.attrib['Name'], 'Visibility': child.attrib['Visibility'], 'Parameters': params})

        if len(attributes) > 0 or len(operations) > 0:
            classes_return[m_class_raw.get('Id')] = {'Name': name, 'Attributes': attributes, 'Operations': operations}

    return classes_return


def parse_diagram_classes(elem):
    m_classes_raw = elem.findall('.//Class')

    classes_return = {}

    for m_class_raw in m_classes_raw:
        x = m_class_raw.get('X')
        y = m_class_raw.get('Y')
        width = m_class_raw.get('Width')
        height = m_class_raw.get('Height')
        id = m_class_raw.get('Id')
        master = m_class_raw.get('Model')
        color = rgb_to_hex(m_class_raw.find('.//FillColor').get('Color'))
        font_shift = parse_font_shift(m_class_raw)
        classes_return[master] = {'x': x, 'y': y, 'width': width, 'height': height, 'color': color, 'id': id, 'shift': font_shift}

    return classes_return


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

def parse_font_shift(elem):
    shift = 0
    for child in elem:
        if child.tag.endswith('ElementFont'):
            shift += int(child.attrib.get('Size'))
    return shift


def rgb_to_hex(rgb_string):
    # Remove the "rgb(" and ")" part and split the remaining string by commas
    rgb_values = rgb_string[4:-1].split(',')

    # Convert each component to an integer
    r, g, b = [int(value) for value in rgb_values]

    # Format the integers as hexadecimal and return the combined string
    return f'#{r:02X}{g:02X}{b:02X}'
def parse(xml_file, output_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # SVG setup
    dwg = svgwrite.Drawing(output_file, profile='full', size=('2000px', '1600px'))

    # Define arrow marker for transitions
    # arrow_marker = dwg.marker(id='arrow', insert=(10, 5), size=(10, 10), orient='auto')
    # arrow_marker.add(dwg.path(d='M0,0 L0,10 L10,5 Z', fill='black'))
    # dwg.defs.add(arrow_marker)

    # Extracting state machine elements
    model_classes = parse_model_classes(root.find('.//Models'))
    diagram_classes = parse_diagram_classes(root.find('.//Diagrams'))
    points = parse_points(root)

    for model_class_name, model_class in model_classes.items():
        print(f'{model_class_name} has {model_class}')

    print('\n')

    for model_class_name, model_class in diagram_classes.items():
        print(f'{model_class_name} has {model_class}')

    combined_classes = {}

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

    for class_id, class_info in combined_classes.items():
        print(f'{class_id}: {class_info}')
    # Parse states and transitions
    # for elem in root.iter():
    #     if 'State' in elem.tag:
    #         class_id = elem.attrib.get('Id', None)
    #         state_name = get_state_name(elem)
    #         state_x = int(elem.attrib.get('X', 0))
    #         state_y = int(elem.attrib.get('Y', 0))
    #         height = int(elem.attrib.get('Height', 0))
    #         width = int(elem.attrib.get('Width', 0))
    #         color = rgb_to_hex(elem.attrib.get('Background', 'rgb(0,0,0)'))
    #         model_children = parse_model_children(elem)
    #         align_to_grid = elem.attrib.get('AlignToGrid')
    #         font_shift_y = int(parse_font_shift(elem))
    #         print(parse_caption_pos(elem))
    #         print(
    #             f'Parsed state: ID={class_id}, Name={state_name}, X={state_x}, Y={state_y}, ModelChildren={model_children}, Width={width}, Height={height}')
    #         if state_x == 0.0 and state_y == 0.0 and class_id and len(model_children) > 0 and align_to_grid is None:
    #             special_states[class_id] = {'name': state_name, 'children': model_children,
    #                                         'caption': parse_caption_pos(elem)}
    #         elif class_id and align_to_grid is None:
    #             print('xd')
    #             states[class_id] = {'name': state_name, 'x': state_x, 'y': state_y, 'children': model_children,
    #                                 'height': height, 'width': width, 'caption': parse_caption_pos(elem),
    #                                 'fontShift': font_shift_y, 'color': color}
    #     elif elem.tag == 'Transition2':
    #         x = int(elem.attrib.get('X', 0))
    #         y = int(elem.attrib.get('Y', 0))
    #         transition_name = elem.attrib.get('Name', '')
    #         id = elem.attrib.get('Id', '')
    #         print(f'Parsed transition: Id={id}, X={x}, Y={y}, Name={transition_name}')
    #         if x and y and id:
    #             transitions.append({'id': id, 'x': x, 'y': y, 'name': transition_name})
    #     elif elem.tag == 'Points':
    #         pointPoints = []
    #         for child in elem.iterchildren():
    #             x = child.attrib.get('X')
    #             y = child.attrib.get('Y')
    #             pointPoints.append({'x': x, 'y': y})
    #         points[elem.getparent().attrib.get('Id')] = pointPoints

    # Integrate special states into their parent states
    # for special_state_id, special_state_info in special_states.items():
    #     for parent_id, parent_info in states.items():
    #         if special_state_info['name'] in parent_info['name']:
    #             print(f'Parent: {parent_info} \n Special: {special_state_info}')
    #             parent_info['children'] += "\n" + special_state_info['children']
    #
    # for class_id, class_info in states.items():
    #     children_lines = class_info['children'].split('\n')
    #     repeat = children_lines.count('')
    #     for i in range(repeat):
    #         children_lines.remove('')
    #
    #     states[class_id]['children'] = ''
    #     for child in children_lines:
    #         states[class_id]['children'] += child + '\n'
    #
    # toRemove = []
    #
    # for transition in transitions:
    #     print(transition['id'])
    #     if points.get(transition['id']) is None:
    #         toRemove.append(transition)
    #
    # for transition in toRemove:
    #     transitions.remove(transition)
    #
    # # Draw states
    for class_id, class_info in combined_classes.items():
        id = class_id
        name = class_info.get('name')
        attributes = class_info.get('attributes')
        operations = class_info.get('operations')
        x = int(class_info['x'])
        y = int(class_info['y'])
        width = int(class_info['width'])
        height = int(class_info['height'])
        color = class_info['color']
        shift = int(class_info['shift'])
        dwg.add(dwg.rect(insert=(x, y), size=(width, height), fill=color, stroke='black'))
        dwg.add(
            dwg.text(class_info['name'], insert=(x + width / 2, y + shift),
                     text_anchor='middle', font_size='11px',
                     font_family='Arial'))
        dwg.add(dwg.line(start=(x, y + shift + 2), end=(x + width, y + shift + 2),
                         stroke='black'))

        write_at = y + shift * 2 + 1.3

        for attribute in attributes:
            dwg.add(dwg.text(attribute.get('Name'), insert=(x + 2, write_at), text_anchor='start',
                                 font_size='10px',
                                 font_family='Arial'))
            write_at += shift

        if write_at != y + shift * 2 + 1.3 and len(operations) > 0:
            dwg.add(dwg.line(start=(x, write_at - shift+2), end=(x + width, write_at - shift+2),
                         stroke='black'))
            write_at += 1

        for operation in operations:
            dwg.add(dwg.text(f'{operation.get('Name')}()', insert=(x + 2, write_at), text_anchor='start',
                             font_size='10px',
                             font_family='Arial'))
            write_at += shift

        previous = None
        for x in range(len(points)):
            actual_points = points[x].get('points')
            for i in range(len(actual_points)):
                if previous is None:
                    previous = actual_points[i]
                    continue

                actual_point = actual_points[i]

                if i == len(actual_points) - 1:
                    dwg.add(dwg.line(start=(previous.get('x'), previous.get('y')),
                                     end=(actual_point.get('x'), actual_point.get('y')), stroke='black'))
                    break

                dwg.add(
                    dwg.line(start=(previous.get('x'), previous.get('y')), end=(actual_point.get('x'), actual_point.get('y')),
                             stroke='black'))

                previous = actual_point
            previous = None
        # if class_info['children']:
        #     children_lines = class_info['children'].split('\n')
        #     children_lines.reverse()
        #     for i, line in enumerate(children_lines):
        #         dwg.add(dwg.text(line, insert=(x + 2, y + font_shift * (i + 1.3)), text_anchor='start',
        #                          font_size='10px',
        #                          font_family='Arial'))
    #
    # # Draw transitions
    # for transition in transitions:
    #     print(transition['id'])
    #     pointsOfTransition = points.get(transition['id'])
    #     previous = None
    #     for i in range(len(pointsOfTransition)):
    #         if previous is None:
    #             previous = pointsOfTransition[i]
    #             continue
    #         actualPoint = pointsOfTransition[i]
    #         if i == len(pointsOfTransition) - 1:
    #             dwg.add(dwg.line(start=(previous.get('x'), previous.get('y')),
    #                              end=(actualPoint.get('x'), actualPoint.get('y')), stroke='black',
    #                              marker_end=arrow_marker.get_funciri()))
    #             break
    #         dwg.add(
    #             dwg.line(start=(previous.get('x'), previous.get('y')), end=(actualPoint.get('x'), actualPoint.get('y')),
    #                      stroke='black'))
    #         previous = actualPoint
    #     dwg.add(dwg.text(transition['name'], insert=(transition['x'] + 120, transition['y'] + 47), text_anchor='middle',
    #                      font_size='10px',
    #                      font_family='Arial'))

    # Save the SVG file
    dwg.save()
    print('SVG file ' + output_file + ' created successfully.')


def main():
    xml_file = 'sumxmls/simple_class_huge.xml'
    output_file = 'class_diagram.svg'

    parse(xml_file, output_file)


if __name__ == "__main__":
    main()
