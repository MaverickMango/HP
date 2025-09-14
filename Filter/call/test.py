import chatbot as cb
import system_prompt
import difflib


def generate_unified_diff(file1, file2):
    """
    生成两个文件的统一格式（Unified Format）差异。

    :param file1: 第一个文件路径
    :param file2: 第二个文件路径
    """
    try:
        # 打开并读取文件内容
        with open(file1, 'r', encoding='utf-8') as f1:
            fromlines = f1.readlines()
        with open(file2, 'r', encoding='utf-8') as f2:
            tolines = f2.readlines()

        # 生成统一格式的差异
        diff = difflib.unified_diff(fromlines, tolines, fromfile=file1, tofile=file2, lineterm='')

        # 打印差异结果
        print(f"{"".join(diff)}")
    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
        

if __name__ == '__main__':
    chatbot = cb.ChatBot(system_prompt=system_prompt.apca7,model='qwq-32b')
    print(chatbot.chat(system_prompt.closure_125_kali,stream=True))
    # generate_unified_diff('D:\\Projects\\python\\LLM\\data\\changesInfo\\Jsoup_4\\properties\\modified_classes\\original\\src\\main\\java\\org\\jsoup\\Entities.java',
    #                       'D:\\Projects\\python\\LLM\\data\\changesInfo\\Jsoup_4\\properties\\modified_classes\\inducing\\src\\main\\java\\org\\jsoup\\nodes\\Entities.java')
    # print("diff --git a/src/main/java/org/jsoup/nodes/Entities.java b/src/main/java/org/jsoup/nodes/Entities.java\nnew file mode 100644\nindex 0000000..37266af\n--- a/src/main/java/org/jsoup/nodes/Entities.java\n+++ b/src/main/java/org/jsoup/nodes/Entities.java\n@@ -43,0 +43,95 @@\n+    static String unescape(String string) {\n+        if (!string.contains(\"&\"))\n+            return string;\n+\n+        StringBuilder accum = new StringBuilder(string.length());\n+        TokenQueue cq = new TokenQueue(string);\n+\n+        // formats dealt with: [&amp] (no semi), [&amp;], [&#123;] (int), &#\n+        while (!cq.isEmpty()) {\n+            accum.append(cq.consumeTo(\"&\"));\n+            if (!cq.matches(\"&\")) { // ran to end\n+                accum.append(cq.remainder());\n+                break;\n+            }\n+            cq.advance(); // past &\n+            String val;\n+            int charval = -1;\n+\n+            boolean isNum = false;\n+            if (cq.matches(\"#\")) {\n+                isNum = true;\n+                cq.consume();\n+            }\n+            val = cq.consumeWord(); // and num!\n+            if (val.length() == 0) {\n+                accum.append(\"&\");\n+                continue;\n+            }\n+            if (cq.matches(\";\"))\n+                cq.advance();\n+\n+            if (isNum) {\n+                try {\n+                    if (val.charAt(0) == 'x' || val.charAt(0) == 'X')\n+                        charval = Integer.valueOf(val.substring(1), 16);\n+                    else\n+                        charval = Integer.valueOf(val, 10);\n+                } catch (NumberFormatException e) {\n+                    // skip\n+                }\n+            } else {\n+                if (full.containsKey(val.toLowerCase()))\n+                    charval = full.get(val.toLowerCase());\n+            }\n+            if (charval == -1 || charval > 0xFFFF) // out of range\n+                accum.append(\"&\").append(val).append(\";\");\n+            else\n+                accum.append((char) charval);\n+        }\n+\n+        return accum.toString();\n+    }")