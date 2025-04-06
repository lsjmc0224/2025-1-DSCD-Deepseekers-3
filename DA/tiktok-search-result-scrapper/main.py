import re
import os
import click
import json
from loguru import logger
from tiktokvideo import TiktokVideo
from tiktokvideo.typing import SearchResult

__title__ = 'TikTok Search Result Scraper'
__version__ = '1.0.0'

@click.command(
    help=__title__
)
@click.version_option(
    version=__version__,
    prog_name=__title__
)
@click.option(
    "--keyword",
    help='Search keyword for TikTok',
    required=True
)
@click.option(
    "--output",
    default='data/',
    help='Directory to store search results'
)
def main(
    keyword: str,
    output: str
): 
    logger.info(f'Starting TikTok search for keyword: {keyword}')

    search_results: SearchResult = TiktokVideo().get_all_videos(keyword)

    if not os.path.exists(output):
        os.makedirs(output)

    output_file = os.path.join(output, f'{keyword}.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(search_results.dict, f, ensure_ascii=False)
    
    logger.info(f'Saved search results for keyword "{keyword}" in {output_file}')

if __name__ == '__main__':
    main()
