import os

import asyncpg
from aiohttp import web


config = {'db': {}, 'query': {}}

MIN_INTERSECT = 2

config['db']['host'] = os.environ.get('DB_HOST', '127.0.0.1')
config['db']['port'] = int(os.environ.get('DB_PORT', 5432))
config['db']['user'] = os.environ.get('DB_USER', 'user')
config['db']['password'] = os.environ.get('DB_PASSWORD', 'password')
config['db']['database'] = os.environ.get('DB_NAME', 'db')

TABLE_NAME__MOVIE = 'tn_movie'
TABLE_NAME__PROFILE_MOVIE = 'tn_profile_movie'
COLUMN_NAME__MOVIE_ID = 'cn_movie_id'
COLUMN_NAME__PROFILE_ID = 'cn_profile_id'
COLUMN_NAME__TITLE = 'cn_title'
COLUMN_NAME__GENRES = 'cn_genres'

QUERY_PARAMS = (
    TABLE_NAME__MOVIE,
    TABLE_NAME__PROFILE_MOVIE,
    COLUMN_NAME__MOVIE_ID,
    COLUMN_NAME__PROFILE_ID,
    COLUMN_NAME__TITLE,
    COLUMN_NAME__GENRES
)

for param in QUERY_PARAMS:
    config['query'][param] = os.environ.get(param.upper(), param[3:])


async def index(request):
    return web.json_response({'dexcription': 'Movies rate system'})


async def movies_rec(request):
    profile_id = request.match_info.get('profile_id', 1)
    rec_query = get_query(int(profile_id))
    result_json = await recommendations(rec_query)
    return web.json_response(result_json)


def get_query(profile_id, min_intersect=MIN_INTERSECT):
    result = """SELECT {cn_movie_id}, {cn_title}, {cn_genres}, _.views FROM {tn_movie}
                RIGHT JOIN(
                    SELECT UNNEST(p_movies.movies) AS {cn_movie_id}, COUNT(1) AS views FROM (
                        SELECT {cn_profile_id}, ARRAY_AGG({cn_movie_id}) AS movies
                            FROM {tn_profile_movie}
                            GROUP BY {cn_profile_id}) AS p_movies
                        WHERE ARRAY_LENGTH(
                            movies & (
                                SELECT ARRAY_AGG({cn_movie_id}) AS movies FROM {tn_profile_movie}
                                WHERE {cn_profile_id} = {target_profile_id}
                             ), 1) > {min_intersect}
                    GROUP BY {cn_movie_id}
                    ORDER BY views DESC) AS _ USING({cn_movie_id})
                WHERE {cn_movie_id} NOT IN (
                    SELECT {cn_movie_id} FROM {tn_profile_movie} 
                    WHERE {cn_profile_id} = {target_profile_id}
                );
    """.format(
            target_profile_id=profile_id,
            min_intersect=min_intersect,
            **config['query']
    )
    return result


async def recommendations(query):
    conn = await asyncpg.connect(**config['db'])
    values = [dict(record) for record in await conn.fetch(query)]
    return values


app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/movies_rec/{profile_id}', movies_rec)


if __name__ == '__main__':
    web.run_app(app, port=5858)
