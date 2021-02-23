import os
import re
import json
import codecs
import pickle
from datetime import datetime
from urllib import request
from bs4 import BeautifulSoup

ALPHA_PATTERN = re.compile(r'^.[a-z]+$')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def touch_dir(path_to_dir):
    if not os.path.exists(path_to_dir):
        os.makedirs(path_to_dir)
    return path_to_dir


def main():
    domains = []
    domains_full = []
    domains_alpha = []
    readme = [
        '# All the world’s top-level domains',
        '',
        'Updated at {}, from [IANA Root Zone Database](http://www.iana.org/domains/root/db)'.format(
            datetime.utcnow().isoformat()),
        '',
        '### domains',
        '',
        '- [domains.txt](data/domains.txt)',
        '- [domains.json](data/domains.json)',
        '',
        '### domains_alpha',
        '',
        '- [domains_alpha.txt](data/domains_alpha.txt)',
        '- [domains_alpha.json](data/domains_alpha.json)',
        '',
        '### domains_full',
        '',
        '- [domains_full.txt](data/domains_full.txt)',
        '- [domains_full.json](data/domains_full.json)',
        '',
    ]

    with request.urlopen('https://www.iana.org/domains/root/db') as f:
        bs = BeautifulSoup(f.read(), features='html.parser')
        trs = bs.find(id='tld-table').tbody.find_all('tr')

        readme.append('### {} records'.format(len(trs)))
        readme.append('')
        readme.append('| Domain | Type | TLD Manager | Info |')
        readme.append('| ------ | ---- | ----------- | ---- |')
        for tr in trs:
            tds = tr.find_all('td')

            str_domain = tds[0].span.a.get_text()
            str_href = tds[0].span.a.get('href')
            str_type = tds[1].get_text()
            str_tld_manager = tds[2].get_text().replace('\n', '')

            domains.append(str_domain)
            domains_full.append(str_domain)

            if re.match(ALPHA_PATTERN, str_domain):
                readme.append('| {} | {} | {} | [Details](https://www.iana.org{}) |'.format(str_domain,
                                                                                            str_type,
                                                                                            str_tld_manager,
                                                                                            str_href))
                domains_alpha.append(str_domain)

            else:
                punycode = str_domain.replace('.', '').encode('punycode').decode('utf-8')
                str_domain_punycode = '.xn--{}'.format(punycode)
                readme.append('| {}<br>{} | {} | {} | [Details](https://www.iana.org{}) |'.format(
                    str_domain,
                    str_domain_punycode,
                    str_type,
                    str_tld_manager,
                    str_href)
                )
                domains_full.append(str_domain_punycode)
                domains_alpha.append(str_domain_punycode)

    # domains
    with codecs.open(os.path.join(DATA_DIR, 'domains.txt'), 'w', encoding='utf-8') as f:
        content = '\n'.join(domains)
        f.write(content)
    with codecs.open(os.path.join(DATA_DIR, 'domains.json'), 'w', encoding='utf-8') as f:
        json.dump(domains, f)

    # domains_full
    with codecs.open(os.path.join(DATA_DIR, 'domains_full.txt'), 'w', encoding='utf-8') as f:
        content = '\n'.join(domains_full)
        f.write(content)
    with codecs.open(os.path.join(DATA_DIR, 'domains_full.json'), 'w', encoding='utf-8') as f:
        json.dump(domains_full, f)

    # domains_alpha
    with codecs.open(os.path.join(DATA_DIR, 'domains_alpha.txt'), 'w', encoding='utf-8') as f:
        content = '\n'.join(domains_alpha)
        f.write(content)
    with codecs.open(os.path.join(DATA_DIR, 'domains_alpha.json'), 'w', encoding='utf-8') as f:
        json.dump(domains_alpha, f)

    # text link pattern
    re_list = []
    for domain in domains:
        re_list.append('\\' + domain)

    text_link_pattern = re.compile(
        r'(?:\.?[a-zA-Z0-9_-]+)+(?:' + '|'.join(re_list) + ')(?::[0-9]+)*(?:/[a-zA-Z0-9_/?&=#%~!@*(),:;+.-]+|/)*'
    )
    with open(os.path.join(DATA_DIR, 'text_link_pattern.pickle'), 'wb') as f:
        pickle.dump(text_link_pattern, f)

    # text link pattern (full)
    re_full_list = []
    for domain in domains_full:
        re_full_list.append('\\' + domain)

    text_link_pattern_full = re.compile(
        r'(?:\.?[a-zA-Z0-9_-]+)+(?:' + '|'.join(re_full_list) + ')(?::[0-9]+)*(?:/[a-zA-Z0-9_/?&=#%~!@*(),:;+.-]+|/)*'
    )
    with open(os.path.join(DATA_DIR, 'text_link_pattern_full.pickle'), 'wb') as f:
        pickle.dump(text_link_pattern_full, f)

    # text link pattern (alpha)
    re_alpha_list = []
    for domain in domains_alpha:
        re_alpha_list.append('\\' + domain)

    text_link_pattern_alpha = re.compile(
        r'(?:\.?[a-zA-Z0-9_-]+)+(?:' + '|'.join(re_alpha_list) + ')(?::[0-9]+)*(?:/[a-zA-Z0-9_/?&=#%~!@*(),:;+.-]+|/)*'
    )
    with open(os.path.join(DATA_DIR, 'text_link_pattern_alpha.pickle'), 'wb') as f:
        pickle.dump(text_link_pattern_alpha, f)

    # README.md
    readme.append('')
    with codecs.open('README.md', 'w', encoding='utf-8') as f:
        content = '\n'.join(readme)
        f.write(content)


if __name__ == "__main__":
    touch_dir(DATA_DIR)
    main()
