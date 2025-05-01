import argparse
import json
with open(r'src\WEB\temp\config.json', 'r') as f:  test = f.read()


# Parse the JSON string into a dictionary
config = json.loads(test)

# Now you can access keys
print(config)  # Output: "value" (from the example input)

