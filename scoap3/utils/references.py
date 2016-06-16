#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

from jinja2 import render_template_to_string

from invenio_records.api import Record
from invenio_search import current_search_client

from inspirehep.modules.search import IQ


class Reference(object):
    """Class used to output reference format in detailed record"""

    def __init__(self, record):
        self.record = record

    def references(self):
        """Reference export for single record in datatables format.

        :returns: list
            List of lists where every item represents a datatables row.
            A row consists of [reference_number, reference, num_citations]
        """

        out = []
        references = self.record.get('references')
        if references:
            refs_to_get_from_es = [
                ref['recid'] for ref in references if ref.get('recid')
            ]
            query = IQ(' OR '.join('recid:' + str(ref)
                                   for ref in refs_to_get_from_es))
            records_from_es = current_search_client.search(
                index='records-hep',
                doc_type='hep',
                body={"query": query.to_dict()},
                size=9999,
                _source=[
                    'control_number',
                    'citation_count',
                    'titles',
                    'earliest_date',
                    'authors',
                    'collaboration',
                    'corporate_author',
                    'publication_info'
                ]
            )['hits']['hits']

            refs_from_es = {
                str(ref['_source']['control_number']): ref['_source'] for ref in records_from_es
            }
            for reference in references:
                row = []
                recid = reference.get('recid')
                ref_record = refs_from_es.get(str(recid)) if recid else None

                if recid and ref_record:
                    ref_record = Record(ref_record)
                    if ref_record:
                        row.append(render_template_to_string(
                            "inspirehep_theme/references.html",
                            record=ref_record,
                            reference=reference
                        ))
                        row.append(ref_record.get('citation_count', ''))
                        out.append(row)
                else:
                    row.append(render_template_to_string(
                        "inspirehep_theme/references.html",
                        reference=reference))
                    row.append('')
                    out.append(row)

        return out
