with raw_source as (
    select * from read_json_auto('raw_data/stream_*.json')
)
select
    session_id::varchar as session_id,
    user_id::varchar as user_id,
    product_id::varchar as product_id,
    action::varchar as click_action,
    timestamp::timestamp as event_timestamp
from raw_source
where event_type = 'clickstream'