# Merges template files together to get the right simulation configuration

# @author  Marek Parucha (WS21/22)
# @author  Martin Dell (WS22/23)
# @date    18.11.2022


from typing import Any
from xml.etree import ElementTree

import constants.services as tempconst
import constants.template_vars as tempkeys
import utils.TemplateUtil as TemplateUtil
from enums.PseudoChangeType import PseudoChangeType
from utils.configuration import SimConfig


def merge_xml_templates(file_paths: 'list[str]', destination_path: str, cfg: SimConfig):
    """
    Merges given XML files together based on the "service" tag.
    The placeholders will get replaced with the simulation parameters.

    Args:
        file_paths (list[str]): Paths of the XML files to merge.
        destination_path (str): Path where to write the merged file to.
        cfg (SimConfig): Simulation configuration.
    """
    replaced_xml_files = []

    # Read files from given paths and replace keys with given values
    for path in file_paths:
        replaced_xml_files.append(TemplateUtil.replace_in_templates(path, cfg, get_service_replacements(cfg)))

    xml_element_tree = None
    for xml_file in replaced_xml_files:
        data = ElementTree.ElementTree(ElementTree.fromstring(xml_file)).getroot()

        for result in data.iter('services'):
            if xml_element_tree is None:
                xml_element_tree = data
                insertion_point = xml_element_tree.findall('.')[0]
            else:
                insertion_point.extend(result)

    # write merged xml file into destination_path
    if xml_element_tree is not None:
        tree = ElementTree.ElementTree(xml_element_tree)

        with open(destination_path, 'w') as f:
            tree.write(f, encoding='unicode')


def get_service_replacements(cfg: SimConfig) -> 'dict[str, Any]':
    """Returns the necessary service placeholder replacements.

    Args:
        cfg (SimConfig): Simulation configuration.

    Returns:
        dict[str, Any]: Replacements used to fill in service placeholder variables.
                        DictKeys correspond to placeholder keys.
    """

    replacements = {
        tempkeys.pseudo_service_key: get_service_class(cfg.pcs.strategy),
    }

    return replacements


def get_service_class(pseudo_change: PseudoChangeType) -> str:
    """Returns the service class name of the pseudonym change strategy.
    """
    if pseudo_change in tempconst.service_classes:
        return tempconst.service_classes[pseudo_change]

    return ''
