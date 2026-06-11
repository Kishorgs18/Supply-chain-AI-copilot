with transactions as (
    select * from {{ ref('stg_transactions') }}
)

select
    order_id,
    customer_id,
    product_id,
    product_category,
    quantity,
    total_amount,
    destination_country,
    order_status,
    event_timestamp as order_placed_at,
    
    -- Feature Engineering for ML Model later
    case 
        when order_status = 'delayed' then 1 
        else 0 
    end as is_delayed

from transactions