TOOLS = [
    {
        "name": "get_transaction",
        "description": (
            "Retrieve transaction details including "
            "amount, customer, merchant, status, "
            "refund status and chargeback information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "integer",
                    "description": "Transaction ID"
                }
            },
            "required": [
                "transaction_id"
            ],
        },
    },

    {
        "name": "get_graph_analysis",
        "description": (
            "Analyze the transaction's graph relationships "
            "including shared devices, IP addresses, "
            "addresses and payment instruments."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "integer",
                    "description": "Transaction ID"
                }
            },
            "required": [
                "transaction_id"
            ],
        },
    },

    {
        "name": "get_transaction_refunds",
        "description": (
            "Retrieve all refunds associated with "
            "a transaction."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "integer",
                    "description": "Transaction ID"
                }
            },
            "required": [
                "transaction_id"
            ],
        },
    },

    {
        "name": "get_cluster_information",
        "description": (
            "Determine whether the transaction belongs "
            "to a coordinated abuse cluster and retrieve "
            "cluster risk and exposure information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "transaction_id": {
                    "type": "integer",
                    "description": "Transaction ID"
                }
            },
            "required": [
                "transaction_id"
            ],
        },
    },
]