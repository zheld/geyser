
class go_types:
    bigint = 'BIGINT'

    integer = 'INTEGER'
    integer_array = "INTEGER[]"

    smallint = "SMALLINT"
    smallintarray = "SMALLINT[]"

    float = 'FLOAT'
    float_array = "FLOAT[]"

    float64 = "FLOAT8"
    int64 = "BIGINT "

    boolean = 'BOOL'
    boolean_array = "BOOL[]"

    vbit = "BIT VARYING"

    pword = ' INTEGER'
    word = ' TEXT'

    text = 'TEXT'
    text_array = "TEXT[]"

    ptext = ' []INTEGER'

    timestamp = 'TIMESTAMP'

    date = 'DATE'

    error = "ERROR"

    money = "DECIMAL (10, 2)"
    exchange_money = "DECIMAL (16, 9)"

    crypto_money = "DECIMAL (15, 8)"
    crypto_money_array = "DECIMAL (15, 8)[]"

    crypto_volume = "DECIMAL (18, 8)"
    crypto_volume_array = "DECIMAL (18, 8)[]"


    @classmethod
    def go_converter( cls, _type ):
        map = { cls.integer: "int",
                cls.smallint: "int",
                cls.float: "float32",
                cls.boolean: "bool",
                cls.pword: "int64",
                cls.ptext: "[]int",
                cls.word: "string",
                cls.text: "string",
                cls.error: "error",
                cls.smallintarray: "[]int",
                cls.integer_array: "[]int",
                cls.float_array: "[]float32",
                cls.boolean_array: "[]bool",
                cls.text_array: "[]string",
                cls.timestamp: "time.Time",
                cls.date: "string",
                cls.vbit: "string",
                cls.money: "float32",
                cls.exchange_money: "float32",
                cls.crypto_money: "float64",
                cls.crypto_money_array: "[]float64",
                cls.crypto_volume: "float64",
                cls.crypto_volume_array: "[]float64",
                cls.float64: "float64",
                cls.int64: "int64",

                }
        if _type in map:
            return map[_type]
        return _type
