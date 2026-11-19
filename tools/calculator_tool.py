import ast
import operator


class CalculatorTool:

    _binary_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    _unary_operators = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }
    _max_expression_length = 200
    _max_exponent = 100

    def run(self, expression: str) -> dict:

        if not isinstance(expression, str) or not expression.strip():
            return {"success": False, "error": "计算表达式不能为空"}

        if len(expression) > self._max_expression_length:
            return {"success": False, "error": "计算表达式过长"}

        try:
            tree = ast.parse(expression, mode="eval")
            result = self._evaluate(tree.body)

            return {"success": True, "result": str(result)}

        except (ArithmeticError, SyntaxError, TypeError, ValueError) as exc:
            return {"success": False, "error": f"计算失败: {str(exc)}"}

    def _evaluate(self, node: ast.AST) -> int | float:

        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(
                node.value, (int, float)
            ):
                raise ValueError("只允许整数和浮点数")
            return node.value

        if isinstance(node, ast.BinOp):
            operator_function = self._binary_operators.get(type(node.op))
            if operator_function is None:
                raise ValueError("包含不支持的运算符")

            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > self._max_exponent:
                raise ValueError("指数绝对值不能超过 100")

            return operator_function(left, right)

        if isinstance(node, ast.UnaryOp):
            operator_function = self._unary_operators.get(type(node.op))
            if operator_function is None:
                raise ValueError("包含不支持的一元运算符")
            return operator_function(self._evaluate(node.operand))

        raise ValueError("表达式只能包含数字和基本算术运算")


if __name__ == "__main__":

    tool = CalculatorTool()

    result = tool.run("12 * 37")

    print(result)
