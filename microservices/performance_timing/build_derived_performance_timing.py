###################################################################
# Script Name   : build_derived_performance_timing.py
#
# Description   : Creates derived.performance_timing, which is a
#               : persistent derived table (PDT)
#
# Requirements  : You must set the following environment variable
#               : to establish credentials for the pgpass user microservice
#
#               : export pguser=<<database_username>>
#               : export pgpass=<<database_password>>
#
#
# Usage         : python build_derived_performance_timing.py
#
#

import os
import psycopg2
import logging

# Logging has two handlers: INFO to stdout and DEBUG to a file handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

if not os.path.exists('logs'):
    os.makedirs('logs')

log_filename = '{0}'.format(os.path.basename(__file__).replace('.py', '.log'))
handler = logging.FileHandler(os.path.join('logs', log_filename),
                              "a", encoding=None, delay="true")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

conn_string = """
dbname='{dbname}' host='{host}' port='{port}' user='{user}' password={password}
""".format(dbname='snowplow',
           host='redshift.analytics.gov.bb.ca',
           port='5439',
           user=os.environ['pguser'],
           password=os.environ['pgpass'])

query = '''
BEGIN;
SET SEARCH_PATH TO derived;
DROP TABLE IF EXISTS performance_timing;
CREATE TABLE performance_timing
  DISTKEY(id)
  SORTKEY(tstamp)
AS (
 
  WITH basic AS (
    SELECT
 
    a.derived_tstamp, -- requires JS tracker 2.6.0 or later
    a.page_urlhost,
    a.page_urlpath,
    a.event,
 
    -- dimensions
 
    a.br_name,
    a.dvce_ismobile,
 
    -- performance timing
 
    b.navigation_start,
    b.redirect_start,
    b.redirect_end,
    b.fetch_start,
    b.domain_lookup_start,
    b.domain_lookup_end,
    b.secure_connection_start,
    b.connect_start,
    b.connect_end,
    b.request_start,
    b.response_start,
    b.response_end,
    b.unload_event_start,
    b.unload_event_end,
    b.dom_loading,
    b.dom_interactive,
    b.dom_content_loaded_event_start,
    b.dom_content_loaded_event_end,
    b.dom_complete,
    b.load_event_start,
    b.load_event_end
 
  FROM atomib.events AS a
 
  INNER JOIN atomib.org_w3_performance_timing_1 AS b
    ON  a.event_id = b.root_id
    AND a.collector_tstamp = b.root_tstamp
 
  WHERE a.event IN ('page_view','page_ping')
    AND a.br_type IN ('Browser', 'Browser (mobile)') -- exclude bots
 
    -- remove unexpected values (affects about 1% of rows)
 
    AND b.navigation_start IS NOT NULL AND b.navigation_start > 0
    AND b.redirect_start IS NOT NULL -- zero is OK
    AND b.redirect_end IS NOT NULL -- zero is OK
    AND b.fetch_start IS NOT NULL AND b.fetch_start > 0
    AND b.domain_lookup_start IS NOT NULL AND b.domain_lookup_start > 0
    AND b.domain_lookup_end IS NOT NULL AND b.domain_lookup_end > 0
    AND b.secure_connection_start IS NOT NULL AND b.secure_connection_start > 0
     -- connect_start is either 0 or NULL
    AND b.connect_end IS NOT NULL AND b.connect_end > 0
    AND b.request_start IS NOT NULL AND b.request_start > 0
    AND b.response_start IS NOT NULL AND b.response_start > 0
    AND b.response_end IS NOT NULL AND b.response_end > 0 AND DATEDIFF(d, a.derived_tstamp, (TIMESTAMP 'epoch' + b.response_end/1000 * INTERVAL '1 second ')) < 365
    AND b.unload_event_start IS NOT NULL AND DATEDIFF(d, a.derived_tstamp, (TIMESTAMP 'epoch' + b.unload_event_start/1000 * INTERVAL '1 second ')) < 365 -- zero is OK
    AND b.unload_event_end IS NOT NULL AND DATEDIFF(d, a.derived_tstamp, (TIMESTAMP 'epoch' + b.unload_event_end/1000 * INTERVAL '1 second ')) < 365 -- zero is OK
    AND b.dom_loading IS NOT NULL AND b.dom_loading > 0
    AND b.dom_interactive IS NOT NULL AND b.dom_interactive > 0
    AND b.dom_content_loaded_event_start IS NOT NULL AND b.dom_content_loaded_event_start > 0
    AND b.dom_content_loaded_event_end IS NOT NULL AND b.dom_content_loaded_event_end > 0
    AND b.dom_complete IS NOT NULL -- zero is OK
    AND b.load_event_start IS NOT NULL -- zero is OK
    AND b.load_event_end IS NOT NULL -- zero is OK
 
  ORDER BY 1,2)
 
  SELECT
 
    id,
    MIN(derived_tstamp) AS tstamp,
    page_urlhost,
    page_urlpath,
 
    SUM(CASE WHEN event = 'page_view' THEN 1 ELSE 0 END) AS pv_count,
    SUM(CASE WHEN event = 'page_ping' THEN 1 ELSE 0 END) AS pp_count,
 
    CASE
      WHEN DATEDIFF(s, MIN(derived_tstamp), MAX(derived_tstamp)) < 10
      THEN ROUND(DATEDIFF(s, MIN(derived_tstamp), MAX(derived_tstamp))/5)*5
      ELSE ROUND(DATEDIFF(s, MIN(derived_tstamp), MAX(derived_tstamp))/10)*10
    END AS time_on_page,
 
    br_name,
    dvce_ismobile,
 
    -- select the first non-zero value
 
    MIN(NULLIF(navigation_start, 0)) AS navigation_start,
    MIN(NULLIF(redirect_start, 0)) AS redirect_start,
    MIN(NULLIF(redirect_end, 0)) AS redirect_end,
    MIN(NULLIF(fetch_start, 0)) AS fetch_start,
    MIN(NULLIF(domain_lookup_start, 0)) AS domain_lookup_start,
    MIN(NULLIF(domain_lookup_end, 0)) AS domain_lookup_end,
    MIN(NULLIF(secure_connection_start, 0)) AS secure_connection_start,
    MIN(NULLIF(connect_start, 0)) AS connect_start,
    MIN(NULLIF(connect_end, 0)) AS connect_end,
    MIN(NULLIF(request_start, 0)) AS request_start,
    MIN(NULLIF(response_start, 0)) AS response_start,
    MIN(NULLIF(response_end, 0)) AS response_end,
    MIN(NULLIF(unload_event_start, 0)) AS unload_event_start,
    MIN(NULLIF(unload_event_end, 0)) AS unload_event_end,
    MIN(NULLIF(dom_loading, 0)) AS dom_loading,
    MIN(NULLIF(dom_interactive, 0)) AS dom_interactive,
    MIN(NULLIF(dom_content_loaded_event_start, 0))
        AS dom_content_loaded_event_start,
    MIN(NULLIF(dom_content_loaded_event_end, 0))
        AS dom_content_loaded_event_end,
    MIN(NULLIF(dom_complete, 0)) AS dom_complete,
    MIN(NULLIF(load_event_start, 0)) AS load_event_start,
    MIN(NULLIF(load_event_end, 0)) AS load_event_end

  FROM basic

  GROUP BY 1,3,4,8,9
  ORDER BY 2

);
'''

with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as curs:
        try:
            curs.execute(query)
        except psycopg2.Error:
            logger.exception((
                'Error: failed to execute the transaction '
                'to prepare the derived.performance_timing PDT'))
        else:
            logger.info((
                'Success: executed the transaction '
                'to prepare the derived.performance_timing PDT'))
