# ---- Helper function ----
def evaluate_condition(value, condition_str):
    try:
        condition_str = condition_str.replace(" ", "")
        operators = [">=", "<=", "==", "!=", ">", "<"]
        for op in operators:
            if op in condition_str:
                threshold = float(condition_str.split(op)[1])
                value = float(value)
                if op == ">=":
                    return value >= threshold
                elif op == "<=":
                    return value <= threshold
                elif op == "==":
                    return value == threshold
                elif op == "!=":
                    return value != threshold
                elif op == ">":
                    return value > threshold
                elif op == "<":
                    return value < threshold
        return False
    except Exception as e:
        print(f"Error evaluating condition: {e}")
        return False