from xulbux import String, FormatCodes


print("'" + String.escape(FormatCodes.to_ansi("[b|br:red](Hello!)")) + "'")
