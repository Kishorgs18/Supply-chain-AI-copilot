with raw_source as (
    select * from read_json_auto('raw_data/stream_*.json')
)
select
    log_id::varchar as log_id,
    warehouse_id::varchar as warehouse_id,
    severity::varchar as severity_level,
    message::varchar as incident_report,
    timestamp::timestamp as event_timestamp
from raw_source
where event_type = 'warehouse_log'