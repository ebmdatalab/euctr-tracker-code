# -*- coding: utf-8 -*-
import urllib.parse as urlparse
import crawl.base as base
from .record import Record

from opentelemetry import trace

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import ConnectionDone
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError


# Module API

def parse_record(res):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("parse_record"):

        span = trace.get_current_span()
        span.set_attribute("url", res.url)
        span.set_attribute("status_code", res.status)

        fields_to_remove = [
            'trial_other',
            'trial_will_this_trial_be_conducted_at_a_single_site_globally',
            'trial_will_this_trial_be_conducted_at_multiple_sites_globally',
            'subject_number_of_subjects_for_this_age_range',
            'subject_trial_has_subjects_under_18',
            'subject_in_utero',
            'subject_preterm_newborn_infants_up_to_gestational_age_37_weeks',
            'subject_newborns_0_27_days',
            'subject_infants_and_toddlers_28_days_23_months',
            'subject_children_2_11years',
            'subject_adolescents_12_17_years',
            'subject_adults_18_64_years',
            'subject_elderly_65_years',
            'subject_women_of_child_bearing_potential_using_contraception',
        ]

        # Init data item
        data = {}

        # Summary

        kpath = '.cellGrey'
        vpath = '.cellGrey+.cellLighterGrey'
        subdata = _parse_dict(res, kpath, vpath)
        # Some trials are badly formed:
        # https://www.clinicaltrialsregister.eu/ctr-search/trial/2012-001258-25/results
        if 'eudract_number' not in subdata:
            return None
        eudract_number = subdata['eudract_number']
        data.update(subdata)
        span.set_attribute("eudract_number", eudract_number)

        key = 'eudract_number_with_country'
        value = '-'.join([eudract_number, res.url.split('/')[-1]])
        data.update({key: value})
        span.set_attribute("eudract_number_with_country", value)

        # Trial results URL

        key = '.summary a::attr(href)'
        value = res.css(key).extract_first()
        if value:
            data['trial_results_url'] = urlparse.urljoin(res.url, value)

        # A. Protocol Information

        ident = 'section-a'
        kpath = '.second'
        vpath = '.second+.third'
        table = _select_table(res, ident)
        subdata = _parse_dict(table, kpath, vpath)
        data.update(subdata)

        # B. Sponsor information

        key = 'sponsors'
        ident = 'section-b'
        kpath = '.second'
        vpath = '.second+.third'
        first = 'name_of_sponsor'
        table = _select_table(res, ident)
        value = _parse_list(table, kpath, vpath, first)
        data.update({key: value})

        # C. Applicant Identification

        # ...

        # D. IMP Identification

        key = 'imps'
        ident = 'section-d'
        kpath = '.second'
        vpath = '.second+.third'
        first = 'imp_role'
        table = _select_table(res, ident)
        value = _parse_list(table, kpath, vpath, first)
        data.update({key: value})

        # D8. Information on Placebo

        key = 'placebos'
        ident = 'section-d8'
        kpath = '.second'
        vpath = '.second+.third'
        first = 'is_a_placebo_used_in_this_trial'
        table = _select_table(res, ident)
        value = _parse_list(table, kpath, vpath, first)
        data.update({key: value})

        # E. General Information on the Trial

        ident = 'section-e'
        kpath = '.second'
        vpath = '.second+.third'
        prefix = 'trial_'
        table = _select_table(res, ident)
        subdata = _parse_dict(table, kpath, vpath, prefix)
        data.update(subdata)

        # F. Population of Trial Subjects

        ident = 'section-f'
        kpath = '.second'
        vpath = '.second+.third'
        prefix = 'subject_'
        table = _select_table(res, ident)
        subdata = _parse_dict(table, kpath, vpath, prefix)
        data.update(subdata)

        code = 'F.1.1'
        key = 'subject_childs'
        value = _parse_value(table, code, index=1)
        subdata[key] = value

        code = 'F.1.2.1'
        key = 'subject_adults'
        value = _parse_value(table, code)
        subdata[key] = value

        code = 'F.1.3.1'
        key = 'subject_elderly'
        value = _parse_value(table, code)
        subdata[key] = value

        data.update(subdata)

        # G. Investigator Networks to be involved in the Trial

        # ...

        # N. Review by the Competent Authority or Ethics Committee

        ident = 'section-n'
        kpath = '.second'
        vpath = '.second+.third'
        table = _select_table(res, ident)
        subdata = _parse_dict(table, kpath, vpath)
        data.update(subdata)

        # P. End of Trial

        ident = 'section-p'
        kpath = '.second'
        vpath = '.second+.third'
        table = _select_table(res, ident)
        subdata = _parse_dict(table, kpath, vpath)
        data.update(subdata)

        # Update data
        data['eudract_number'] = eudract_number

        # Remove data
        for key in fields_to_remove:
            if key in data:
                del data[key]

        # Create record
        record = Record.create(res.url, data)

        return record


def trial_errback(failure):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("trial_errback"):
        span = trace.get_current_span()

        request = failure.request
        span.set_attribute("url", request.url)

        eudract_number_with_country = '-'.join([request.url.split('/')[-2], request.url.split('/')[-1]])
        span.set_attribute("eudract_number_with_country", eudract_number_with_country)

        if failure.check(HttpError):
            span.set_attribute('error', 'HttpError')
            span.set_attribute("status_code", failure.value.response.status)

        elif failure.check(DNSLookupError):
            span.set_attribute('error', 'DNSLookupError')

        elif failure.check(ConnectionDone):
            span.set_attribute('error', 'ConnectionDone')

        elif failure.check(TimeoutError, TCPTimedOutError):
            span.set_attribute('error', 'TimeoutError')


def searchpage_errback(failure):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("searchpage_errback"):
        span = trace.get_current_span()

        request = failure.request
        span.set_attribute("url", request.url)

        if failure.check(HttpError):
            span.set_attribute('error', 'HttpError')
            span.set_attribute("status_code", failure.value.response.status)

        elif failure.check(DNSLookupError):
            span.set_attribute('error', 'DNSLookupError')

        elif failure.check(ConnectionDone):
            span.set_attribute('error', 'ConnectionDone')

        elif failure.check(TimeoutError, TCPTimedOutError):
            span.set_attribute('error', 'TimeoutError')


# Internal

def _select_table(sel, ident):
    return sel.xpath('//table[@id="%s"]' % ident)


def _parse_dict(sel, kpath, vpath, prefix=None):
    """parse data from title-paragraph like html.
    """
    data = {}
    key = None
    value = None
    for sel in sel.css('%s, %s' % (kpath, vpath)):
        if sel.css(kpath):
            key = None
            value = None
            texts = sel.xpath('.//text()').extract()
            if texts:
                key = base.helpers.slugify(' '.join(texts).strip())
        else:
            if key is not None:
                value = None
                texts = sel.xpath('.//text()').extract()
                if texts:
                    value = ' '.join(texts).strip()
        if key and value:
            if prefix:
                key = base.helpers.slugify(prefix + key)
            data[key] = value
    return data


def _parse_list(sel, kpath, vpath, first):
    """parse data from title-paragraph like html.
    """
    data = []
    item = {}
    key = None
    value = None
    for sel in sel.css('%s, %s' % (kpath, vpath)):
        if sel.css(kpath):
            key = None
            value = None
            texts = sel.xpath('.//text()').extract()
            if texts:
                key = base.helpers.slugify(' '.join(texts).strip())
        else:
            if key is not None:
                value = None
                texts = sel.xpath('.//text()').extract()
                if texts:
                    value = ' '.join(texts).strip()
        if key and value:
            item[key] = value
        if key == first and value is None and item:
            data.append(item)
            item = {}
    if item:
        data.append(item)
    return data


def _parse_value(sel, code, index=0, default=None):
    try:
        tr = sel.xpath('//td[text() = "%s"]/..' % code)[index]
        td = tr.xpath('td')[2]
        value = ' '.join(td.xpath('.//text()').extract()).strip()
        return value
    except Exception:
        return default
