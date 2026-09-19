# import ast

# class SkeletonTransformer(ast.NodeTransformer):
#     """Walks the AST and replaces function/method bodies with a '...' placeholder."""
    
#     def visit_FunctionDef(self, node):
#         # 1. Keep the docstring if it exists for context
#         docstring = ast.get_docstring(node)
        
#         # 2. Replace the entire body with '...' (Elision)
#         if docstring:
#             node.body = [ast.Expr(value=ast.Constant(value=docstring)), ast.Expr(value=ast.Constant(value=...))]
#         else:
#             node.body = [ast.Expr(value=ast.Constant(value=...))]
            
#         return node

#     def visit_AsyncFunctionDef(self, node):
#         return self.visit_FunctionDef(node)

# def generate_skeleton(source_code: str) -> str:
#     # Parse the raw code into a syntax tree
#     tree = ast.parse(source_code)
#     print("The value of tree is: ",tree)
    
#     # Strip the bodies
#     transformer = SkeletonTransformer()
#     modified_tree = transformer.visit(tree)
#     # Fix line numbers and convert the tree back into clean code
#     print("this is the line ",ast.fix_missing_locations(modified_tree))
#     return ast.unparse(modified_tree)

# # --- Example Usage ---
# huge_code = """
# class DataProcessor:
#     def __init__(self, database_url: str):
#         \"\"\"Initialize the connection.\"\"\"
#         self.db = connect(database_url)
#         self.cache = {}
#         # Imagine 50 lines of complex setup code here...

#     def process_large_file(self, file_path: str) -> dict:
#         \"\"\"Parses and aggregates data.\"\"\"
#         result = {}
#         with open(file_path) as f:
#             for line in f:
#                 # Imagine 500 lines of heavy algorithmic processing logic here...
#                 pass
#         return result
# """

# # print(generate_skeleton(huge_code))


# tree = ast.parse(huge_code)

# class_node = tree.body[0]
# print(print("hello"))




# a =2 
# print(a.__int__)


# def process_data():
#     print("hello world") 


# process_data()


"""


1520. Maximum Number of Non-Overlapping Substrings
Given a string s of lowercase letters, you need to find the maximum number of non-empty substrings of s that meet the following conditions:

The substrings do not overlap, that is for any two substrings s[i..j] and s[x..y], either j < x or i > y is true.
A substring that contains a certain character c must also contain all occurrences of c.
Find the maximum number of substrings that meet the above conditions. If there are multiple solutions with the same number of substrings, return the one with minimum total length. It can be shown that there exists a unique solution of minimum total length.

Notice that you can return the substrings in any order.

Example 1:

Input: s = "adefaddaccc"
Output: ["e","f","ccc"]
Explanation: The following are all the possible substrings that meet the conditions:
[
  "adefaddaccc"
  "adefadda",
  "ef",
  "e",
  "f",
  "ccc",
]
If we choose the first string, we cannot choose anything else and we'd get only 1. If we choose "adefadda", we are left with "ccc" which is the only one that doesn't overlap, thus obtaining 2 substrings. Notice also, that it's not optimal to choose "ef" since it can be split into two. Therefore, the optimal way is to choose ["e","f","ccc"] which gives us 3 substrings. No other solution of the same number of substrings exist.
Example 2:

Input: s = "abbaccd"
Output: ["d","bb","cc"]
Explanation: Notice that while the set of substrings ["d","abba","cc"] also has length 3, it's considered incorrect since it has larger total length.
 

Constraints:

1 <= s.length <= 105
s contains only lowercase English letters.

"""

def count(string: str)->dict:
    dic = {}
    for i in string:
        if i in dic:
            dic[i] = dic[i]+1
        else:
            dic[i] = 1

    return dic



# approach is dp + 

class Solution:
    def maxNumOfSubstrings(self, s: str) -> list[str]:
        