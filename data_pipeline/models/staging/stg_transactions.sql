with raw_source as (
    select * from read_json_auto('raw_data/stream_*.json')
)
select
    order_id::varchar as order_id,
    customer_id::varchar as customer_id,
    product_id::varchar as product_id,
    category::varchar as product_category,
    quantity::integer as quantity,
    total_amount::double as total_amount,
    destination_country::varchar as destination_country,
    status::varchar as order_status,
    timestamp::timestamp as event_timestamp
from raw_source
where event_type = 'transaction'