from xulbux import String, FormatCodes

# WIP

print("'" + String.escape(FormatCodes.to_ansi("[b|br:red](Hello!)")) + "'")
print("'" + String.escape(FormatCodes.to_ansi("[b|bg:red](Hello!)")) + "'")
print("'" + String.escape(FormatCodes.to_ansi("[b|br:bg:red](Hello!)")) + "'")
