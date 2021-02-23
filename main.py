import re
import codecs
from datetime import datetime
from urllib import request
from bs4 import BeautifulSoup

ALPHA_PATTERN = re.compile(r'^.[a-z]+$')


def main():
    domains = []
    domains_alpha = []
    readme = [
        '# All the world’s top-level domains',
        '',
        'Updated at {}, from [IANA Root Zone Database](http://www.iana.org/domains/root/db)'.format(
            datetime.utcnow().isoformat()),
        '',
        '- [domains.txt](domains.txt)',
        '- [domains_alpha.txt](domains_alpha.txt)',
    ]

    with request.urlopen('https://www.iana.org/domains/root/db') as f:
        bs = BeautifulSoup(f.read(), features='html.parser')
        trs = bs.find(id='tld-table').tbody.find_all('tr')

        readme.append('')
        readme.append('{} records:'.format(len(trs)))
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
                domains_alpha.append(str_domain_punycode)

    # domains.txt
    with codecs.open('domains.txt', 'w', encoding='utf-8') as f:
        content = '\n'.join(domains)
        f.write(content)

    # domains_alpha.txt
    with codecs.open('domains_alpha.txt', 'w', encoding='utf-8') as f:
        content = '\n'.join(domains_alpha)
        f.write(content)

    # README.md
    readme.append('')
    with codecs.open('README.md', 'w', encoding='utf-8') as f:
        content = '\n'.join(readme)
        f.write(content)


if __name__ == "__main__":
    main()
