from mediawiki_parser import preprocessorParser
from copyright_evidence.items import Study, Method
import logging
import py3compat
import collections

def parse_templates_from_text(txt):
    '''
    Parses all templates from the mediawiki text.
    '''
    templates = collections.defaultdict(list)
    def substitute_template(node):
        page_name = node.value[0].value.strip()
        parameters = {}
        if len(node.value) > 1:
            for parameter in node.value[1].value:
                if isinstance(parameter.value, py3compat.string_types) or \
                   len(parameter.value) == 1:
                    # It is a standalone parameter
                    parameters['%s' % parameter.value] = None
                elif len(parameter.value) == 2 and \
                     parameter.value[0].tag == 'parameter_name' and \
                     parameter.value[1].tag == 'parameter_value':
                    parameter_name = parameter.value[0].value
                    parameter_value = parameter.value[1].leaf()
                    parameters['%s' % parameter_name] = '%s' % parameter_value
                else:
                    raise Exception("Bad AST shape!")
        templates[page_name].append(parameters)
        # Once the template has been parsed, remove it
        # from the text.
        node.value = ''

    def noop(node):
        pass

    custom_parser = preprocessorParser.make_parser({
        'substitute_template': substitute_template,
        'substitute_template_parameter': noop,
        'substitute_named_entity': noop,
        'substitute_numbered_entity': noop
    })
    parsed_text = custom_parser.parse(txt)
    return parsed_text.leaf().strip(), dict(templates)

def parse_item_from_templates(templates):
    '''
    Tries to guess the type of page and returns
    the scrapy item.
    '''
    item = None
    keys = set(templates.keys())
    if len(keys) == 0:
        raise Exception('Unable to parse templates %s' % templates.keys())
    elif len(keys) == 1:
        key = keys.pop()
        recognized_keys = [
            'Data Source',
            'Author',
            'Discipline',
            'Country',
            'Level of Aggregation',
            'Industry',
            'REF Unit of Assessment',
            'Evidence Based Policy',
            'Fundamental Issue']
        if key == 'Source':
            logging.debug('Parsing study (1)')
            assert len(templates['Source']) == 1
            item = Study()
            item['source'] = parse_source_from_template(templates['Source'][0])
        elif key == 'Method':
            logging.debug('Parsing method (1)')
            assert len(templates['Method']) == 1
            item =  generic_parse_template_(templates['Method'][0], Method())
        elif key in recognized_keys:
            pass
        else:
            raise Exception('Unable to parse template %s' % key)
    elif len(keys) == 2:
        if keys == set(['Source', 'MainSource']):
            logging.debug('Parsing study (2)')
            assert len(templates['Source']) == 1
            item = Study()
            item['source'] = parse_source_from_template(templates['Source'][0])
        else:
            raise Exception('Unable to parse templates %s' % templates.keys())
    elif len(keys) == 3:
        if keys == set(['Source', 'MainSource', 'Dataset']):
            logging.debug('Parsing study (3)')
            assert len(templates['Source']) == 1
            item = Study()
            item['source'] = parse_source_from_template(templates['Source'][0])
            item['dataset'] = []
            for dataset in templates['Dataset']:
                item['dataset'].append(parse_source_from_template(dataset))
        else:
            raise Exception('Unable to parse templates %s' % templates.keys())
    else:
        raise Exception('Unable to parse templates %s' % templates.keys())
    return item

def generic_parse_template_(tmpl, item, associations = {}):
    for key, value in tmpl.iteritems():
        if key in associations:
            item[associations[key]] = value
        else:
            item[key.strip().lower().replace(' ', '_')] = value
    return item

def parse_dataset_from_template(tmpl):
    '''
    Parses a Dataset item from the corresponding templates.
    '''
    return generic_parse_template_(tmpl, Study.Dataset())

def parse_source_from_template(tmpl):
    '''
    Parses a Source item from the corresponding templates.
    '''
    # List of customly associated templates fields.
    # Case sensitive.
    SOURCE_ASSOCIATIONS = {
        'Intervention-Response': 'intervention_response',
        'EvidenceBasedPolicy': 'evidence_based_policy',
        'FundamentalIssue': 'fundamental_issue',
        'Cross-country': 'cross_country'
    }
    return generic_parse_template_(tmpl, Study.Source(), SOURCE_ASSOCIATIONS)
