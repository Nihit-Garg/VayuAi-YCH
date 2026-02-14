from predict_next_5 import predict_next_n
import contextlib
import io

f = io.StringIO()
with contextlib.redirect_stdout(f):
    predict_next_n()
out = f.getvalue()
import re
match = re.search(r"Next 5 Predicted Values: (\[.*?\])", out, re.DOTALL)
if match:
    print(match.group(1))
else:
    print("Could not parse output")
