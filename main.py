import json, unittest, datetime

# Read all three JSON files
with open("./json/data1.json","r") as f:
    jsonData1 = json.load(f)
with open("./json/data2.json","r") as f:
    jsonData2 = json.load(f)
with open("./json/data-result.json","r") as f:
    jsonExpectedResult = json.load(f)


def convertFromFormat1(jsonObject):
    """
    Format 1 has a flat location string like "japan/tokyo/area/factory/section"
    and uses 'operationStatus' + 'temp' for data fields.
    We split the location string and rename the data fields to match unified format.
    """
    locationParts = jsonObject["location"].split("/")

    result = {
        "deviceID": jsonObject["deviceID"],
        "deviceType": jsonObject["deviceType"],
        "timestamp": jsonObject["timestamp"],  # already in milliseconds since epoch
        "location": {
            "country": locationParts[0],
            "city":    locationParts[1],
            "area":    locationParts[2],
            "factory": locationParts[3],
            "section": locationParts[4],
        },
        "data": {
            "status":      jsonObject["operationStatus"],  # rename from operationStatus
            "temperature": jsonObject["temp"],             # rename from temp
        },
    }
    return result


def convertFromFormat2(jsonObject):
    """
    Format 2 stores device info in a nested 'device' object, has an ISO 8601
    timestamp, and spreads location fields at the top level.
    We flatten device info, convert the timestamp to ms since epoch, and nest location.
    """
    # Convert ISO 8601 timestamp "2021-06-23T10:57:17.783Z" → milliseconds since epoch
    dt = datetime.datetime.strptime(jsonObject["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
    timestamp_ms = round((dt - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

    result = {
        "deviceID":   jsonObject["device"]["id"],
        "deviceType": jsonObject["device"]["type"],
        "timestamp":  timestamp_ms,
        "location": {
            "country": jsonObject["country"],
            "city":    jsonObject["city"],
            "area":    jsonObject["area"],
            "factory": jsonObject["factory"],
            "section": jsonObject["section"],
        },
        "data": jsonObject["data"],  # already in the correct shape {status, temperature}
    }
    return result


def main(jsonObject):
    """Route to the correct converter based on which format the input uses."""
    if jsonObject.get("device") is None:
        return convertFromFormat1(jsonObject)
    else:
        return convertFromFormat2(jsonObject)


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

class TestSolution(unittest.TestCase):

    def test_sanity(self):
        """The expected result file loads correctly."""
        result = json.loads(json.dumps(jsonExpectedResult))
        self.assertEqual(result, jsonExpectedResult)

    def test_dataType1(self):
        """Format 1 converts to the unified format correctly."""
        result = main(jsonData1)
        self.assertEqual(result, jsonExpectedResult, "Converting from Type 1 failed")

    def test_dataType2(self):
        """Format 2 converts to the unified format correctly."""
        result = main(jsonData2)
        self.assertEqual(result, jsonExpectedResult, "Converting from Type 2 failed")


if __name__ == "__main__":
    unittest.main()