
BASE_INSTRUCTION = """As an AI debugger, your duty is to generate a refined version for each buggy function. Do not response anything else except the refined version of buggy function."""

DIFF_INSTRUCTION = """As an AI debugger, your duty is to generate a diff patch for each buggy function. Do not response anything else except the diff patch of buggy function."""

LOCATED_INSTRUCTION = """As an AI debugger, your duty is to generate code snippets to fill the chunks marked as `<Chunk_For_Modification>` in each provided buggy function. Do not response anything else except the generated code snippets."""

HYBRID_INSTRUCTION = """As an AI debugger, your duty is to generate a refined version for each buggy function, where the buggy chunks are marked as `<Chunk_For_Modification>` in each provided buggy function. Do not response anything else except the refined version of buggy function."""

GENERAL_INSTRUCTION = """You are ChatGPT, a large language model trained by OpenAI.
Carefully heed the user's instructions.
Respond using Markdown.
Current Date: 2024/2/4 21:11:20"""

AGENT_INSTRUCTION = """As an AI debugger, your duty is to generate a refined version of the buggy function for each bug report. Do not response anything else except the refined version of buggy function."""

REVERSE_INSTRUCTION = """As an AI debugger, your duty is to generate the corrected code snippets for the buggy locations via referring the given bug report. Do not response anything else except the generated code snippets."""

MERGE_INSTRUCTION = """As an AI merger, your duty is to generate a merged program via applying the given patch to the given function. Do not response anything else except the merged function."""

USER_PROMPT = """```{LANGUAGE}
{BUGGY_CODE}
```"""

GO_PROMPT = """```go
{BUGGY_CODE}
```"""


AGENT_PROMPT = """### Buggy function comment:
{BUGGY_COMMENT}

### Error message from JUnit test:
{ERROR_MESSAGE}

### Failed JUnit test:
```java
{FAILED_TEST}
```

### Buggy function (You need to generate a fixed version of this program):
```java
{BUGGY_CODE}
```"""

AGENT_PROMPT_DIFF = """### Buggy function comment:
{BUGGY_COMMENT}

### Error message from JUnit test:
{ERROR_MESSAGE}

### Failed JUnit test:
```java
{FAILED_TEST}
```

### Buggy function (You need to generate a diff patch of this program):
```java
{BUGGY_CODE}
```"""

ZERO_PROMPT = """{BUGGY_CODE}"""

NONE_INSTRUCTION = "\n\nDo not generate any natural language question, explanation, or description."

FREE_INSTRUCTION = "\n\nThis is a bug-free code snippet. Do not generate any natural language question, explanation, or description."

EXAMPLE_INPUT_CPP_REFINE = """```cpp
class Solution {
public:

vector<int> countsort(vector<int> &nums)
{
    int n = nums.size();
    map<int, int> m;
    for (int i = 0; i < n; i++ )
        m[nums[i]]++;

    nums.clear();
    for (auto it : m)
    {
        int cnt = it.second;
        while (cnt--)
        {
            nums.push_back(it.first);
        }
    }
    return nums;
}

int maximumGap(vector<int> &nums)
{
    int n = nums.size();
    if (n < 2)
        return 0;
    vector<int> sortednums = countsort(nums);

    int maxgap = INT_MIN;
    for (int i = 1; i <= n; i++)
    {
        int currgap = sortednums[i] - sortednums[i - 1];
        maxgap = max(maxgap, currgap);
    }

    return maxgap;
}
};
```"""

EXAMPLE_OUTPUT_CPP_DIFF = """```diff
@@
     vector<int> sortednums = countsort(nums);

     int maxgap = INT_MIN;
-    for (int i = 1; i <= n; i++)
+    for (int i = 1; i < n; i++)
     {
         int currgap = sortednums[i] - sortednums[i - 1];
         maxgap = max(maxgap, currgap);
```"""

EXAMPLE_OUTPUT_CPP_BASE = """```cpp
class Solution {
public:

vector<int> countsort(vector<int> &nums)
{
    int n = nums.size();
    map<int, int> m;
    for (int i = 0; i < n; i++ )
        m[nums[i]]++;

    nums.clear();
    for (auto it : m)
    {
        int cnt = it.second;
        while (cnt--)
        {
            nums.push_back(it.first);
        }
    }
    return nums;
}

int maximumGap(vector<int> &nums)
{
    int n = nums.size();
    if (n < 2)
        return 0;
    vector<int> sortednums = countsort(nums);

    int maxgap = INT_MIN;
    for (int i = 1; i < n; i++)
    {
        int currgap = sortednums[i] - sortednums[i - 1];
        maxgap = max(maxgap, currgap);
    }

    return maxgap;
}
};
```"""

EXAMPLE_OUTPUT_CPP_MIX = """```diff
@@
     vector<int> sortednums = countsort(nums);

     int maxgap = INT_MIN;
-    for (int i = 1; i <= n; i++)
+    for (int i = 1; i < n; i++)
     {
         int currgap = sortednums[i] - sortednums[i - 1];
         maxgap = max(maxgap, currgap);
```

```cpp
class Solution {
public:

vector<int> countsort(vector<int> &nums)
{
    int n = nums.size();
    map<int, int> m;
    for (int i = 0; i < n; i++ )
        m[nums[i]]++;

    nums.clear();
    for (auto it : m)
    {
        int cnt = it.second;
        while (cnt--)
        {
            nums.push_back(it.first);
        }
    }
    return nums;
}

int maximumGap(vector<int> &nums)
{
    int n = nums.size();
    if (n < 2)
        return 0;
    vector<int> sortednums = countsort(nums);

    int maxgap = INT_MIN;
    for (int i = 1; i < n; i++)
    {
        int currgap = sortednums[i] - sortednums[i - 1];
        maxgap = max(maxgap, currgap);
    }

    return maxgap;
}
};
```"""


EXAMPLE_INPUT_JAVA_REFINE = """```java
class Solution {
    public String[] findRelativeRanks(int[] score) {
         int n=score.length;
        PriorityQueue<Integer> pq=new PriorityQueue<>((a,b)-> score[b]-score[a]);
        for(int i=0;i<n;i++) pq.add(i);
        String[] ans = null;
        int i=1;
        while(!pq.isEmpty()){
            int idx=pq.poll();
            if(i=1) { ans[idx]="Gold Medal"; i++;} 
            else if(i=2) { ans[idx]="Silver Medal"; i++;} 
            else if(i=3) { ans[idx]="Bronze Medal"; i++;} 
            else ans[idx]=Integer.toString(i++);
        }
        return reorderArray(ans);  
    }

    private String[] reorderArray(String[] ranks){
        
    }
}
```"""

EXAMPLE_OUTPUT_JAVA_DIFF = """```diff
@@
         int n=score.length;
         PriorityQueue<Integer> pq=new PriorityQueue<>((a,b)-> score[b]-score[a]);
         for(int i=0;i<n;i++) pq.add(i);
-        String[] ans = null;
+        String[] ans = new String[n];
         int i=1;
         while(!pq.isEmpty()){
             int idx=pq.poll();
@@
             else ans[idx]=Integer.toString(i++);
         }
         return ans;  
     }

-    private String[] reorderArray(String[] ranks){
-        
-    }
 }
```"""

EXAMPLE_OUTPUT_JAVA_BASE = """```java
class Solution {
    public String[] findRelativeRanks(int[] score) {
         int n=score.length;
        PriorityQueue<Integer> pq=new PriorityQueue<>((a,b)-> score[b]-score[a]);
        for(int i=0;i<n;i++) pq.add(i);
        String[] ans = new String[n];
        int i=1;
        while(!pq.isEmpty()){
            int idx=pq.poll();
            if(i=1) { ans[idx]="Gold Medal"; i++;} 
            else if(i=2) { ans[idx]="Silver Medal"; i++;} 
            else if(i=3) { ans[idx]="Bronze Medal"; i++;} 
            else ans[idx]=Integer.toString(i++);
        }
        return reorderArray(ans);  
    }
}
```"""

EXAMPLE_OUTPUT_JAVA_MIX = """```diff
@@
         int n=score.length;
         PriorityQueue<Integer> pq=new PriorityQueue<>((a,b)-> score[b]-score[a]);
         for(int i=0;i<n;i++) pq.add(i);
-        String[] ans = null;
+        String[] ans = new String[n];
         int i=1;
         while(!pq.isEmpty()){
             int idx=pq.poll();
@@
             else ans[idx]=Integer.toString(i++);
         }
         return ans;  
     }

-    private String[] reorderArray(String[] ranks){
-        
-    }
 }
```

```java
class Solution {
    public String[] findRelativeRanks(int[] score) {
         int n=score.length;
        PriorityQueue<Integer> pq=new PriorityQueue<>((a,b)-> score[b]-score[a]);
        for(int i=0;i<n;i++) pq.add(i);
        String[] ans = new String[n];
        int i=1;
        while(!pq.isEmpty()){
            int idx=pq.poll();
            if(i=1) { ans[idx]="Gold Medal"; i++;} 
            else if(i=2) { ans[idx]="Silver Medal"; i++;} 
            else if(i=3) { ans[idx]="Bronze Medal"; i++;} 
            else ans[idx]=Integer.toString(i++);
        }
        return reorderArray(ans);  
    }
}
```"""



EXAMPLE_INPUT_PYTHON_REFINE = """```python3
class Solution:
    def addBinary(self, A, B):
        res = []
        carry = 0
        while A or B or carry:
            carry += (A or [0]).pop() + (B or [0]).pop()
            res.append(carry & 1)
            carry = carry >> 1
        return res[::-1][1]  

    def addNegabinary(self, A, B):
        res = []
        carry = 0
        while A or B or carry:
            carry += (A or [0]).pop() + (B or [0]).pop()
            res.append(carry & 1)
            carry = -(carry >> 1)
        while len(res) > 1 and res[-1] == 0:
            res.pop()
        return res[::-1][1]
```"""

EXAMPLE_OUTPUT_PYTHON_DIFF = """```diff
@@
             carry += (A or [0]).pop() + (B or [0]).pop()
             res.append(carry & 1)
             carry = carry >> 1
-        return res[::-1][1]  
+        return res[::-1]  

     def addNegabinary(self, A, B):
         res = []
@@
             carry = -(carry >> 1)
         while len(res) > 1 and res[-1] == 0:
             res.pop()
-        return res[::-1][1]
+        return res[::-1]
```"""

EXAMPLE_OUTPUT_PYTHON_BASE = """```python3
class Solution:
    def addBinary(self, A, B):
        res = []
        carry = 0
        while A or B or carry:
            carry += (A or [0]).pop() + (B or [0]).pop()
            res.append(carry & 1)
            carry = carry >> 1
        return res[::-1]

    def addNegabinary(self, A, B):
        res = []
        carry = 0
        while A or B or carry:
            carry += (A or [0]).pop() + (B or [0]).pop()
            res.append(carry & 1)
            carry = -(carry >> 1)
        while len(res) > 1 and res[-1] == 0:
            res.pop()
        return res[::-1]
```"""

EXAMPLE_OUTPUT_PYTHON_MIX = """```diff
@@
             carry += (A or [0]).pop() + (B or [0]).pop()
             res.append(carry & 1)
             carry = carry >> 1
-        return res[::-1][1]  
+        return res[::-1]  

     def addNegabinary(self, A, B):
         res = []
@@
             carry = -(carry >> 1)
         while len(res) > 1 and res[-1] == 0:
             res.pop()
-        return res[::-1][1]
+        return res[::-1]
```

```python3
class Solution:
    def addBinary(self, A, B):
        res = []
        carry = 0
        while A or B or carry:
            carry += (A or [0]).pop() + (B or [0]).pop()
            res.append(carry & 1)
            carry = carry >> 1
        return res[::-1]

    def addNegabinary(self, A, B):
        res = []
        carry = 0
        while A or B or carry:
            carry += (A or [0]).pop() + (B or [0]).pop()
            res.append(carry & 1)
            carry = -(carry >> 1)
        while len(res) > 1 and res[-1] == 0:
            res.pop()
        return res[::-1]
```"""

EXAMPLE_INPUT_CPP_REPAIR = """```cpp
class Solution {
public:

vector<int> countsort(vector<int> &nums)
{
    int n = nums.size();
    map<int, int> m;
    for (int i = 0; i < n; i++ )
        m[nums[i]]++;

    nums.clear();
    for (auto it : m)
    {
        int cnt = it.second;
        while (cnt--)
        {
            nums.push_back(it.first);
        }
    }
    return nums;
}

int maximumGap(vector<int> &nums)
{
    int n = nums.size();
    if (n < 2)
        return 0;
    vector<int> sortednums = countsort(nums);

    int maxgap = INT_MIN;
<Chunk_For_Modification>
    {
        int currgap = sortednums[i] - sortednums[i - 1];
        maxgap = max(maxgap, currgap);
    }

    return maxgap;
}
};
```"""

EXAMPLE_OUTPUT_CPP_LOCATED = """```cpp
for (int i = 1; i < n; i++)
```"""

EXAMPLE_INPUT_FUNC_REFINE = """```java
public static double linearCombination(final double[] a, final double[] b)
        throws DimensionMismatchException {
        final int len = a.length;
        if (len != b.length) {
             throw new DimensionMismatchException(len, b.length);
         }
 
             // Revert to scalar multiplication.
 
         final double[] prodHigh = new double[len];
         double prodLowSum = 0;

        for (int i = 0; i < len; i++) {
            final double ai = a[i];
            final double ca = SPLIT_FACTOR * ai;
            final double aHigh = ca - (ca - ai);
            final double aLow = ai - aHigh;

            final double bi = b[i];
            final double cb = SPLIT_FACTOR * bi;
            final double bHigh = cb - (cb - bi);
            final double bLow = bi - bHigh;
            prodHigh[i] = ai * bi;
            final double prodLow = aLow * bLow - (((prodHigh[i] -
                                                    aHigh * bHigh) -
                                                   aLow * bHigh) -
                                                  aHigh * bLow);
            prodLowSum += prodLow;
        }

        // if(len == 1)
        // {
        //     return a[0]*b[0];
        // }
        final double prodHighCur = prodHigh[0];
        // double prodHighNext = len > 1 ? prodHigh[1] : 0;
        double prodHighNext = prodHigh[1];
        // if(len == 1)
        // {
        //     return prodHighCur;
        // }
        double sHighPrev = prodHighCur + prodHighNext;
        double sPrime = sHighPrev - prodHighNext;
        double sLowSum = (prodHighNext - (sHighPrev - sPrime)) + (prodHighCur - sPrime);

        final int lenMinusOne = len - 1;
        for (int i = 1; i < lenMinusOne; i++) {
            prodHighNext = prodHigh[i + 1];
            final double sHighCur = sHighPrev + prodHighNext;
            sPrime = sHighCur - prodHighNext;
            sLowSum += (prodHighNext - (sHighCur - sPrime)) + (sHighPrev - sPrime);
            sHighPrev = sHighCur;
        }

        double result = sHighPrev + (prodLowSum + sLowSum);

        if (Double.isNaN(result)) {
            // either we have split infinite numbers or some coefficients were NaNs,
            // just rely on the naive implementation and let IEEE754 handle this
            result = 0;
            for (int i = 0; i < len; ++i) {
                result += a[i] * b[i];
            }
        }

        return result;
    }
```"""

EXAMPLE_OUTPUT_FUNC_BASE = """```java
public static double linearCombination(final double[] a, final double[] b)
        throws DimensionMismatchException {
        final int len = a.length;
        if (len != b.length) {
             throw new DimensionMismatchException(len, b.length);
         }
 
         if (len == 1) {
             // Revert to scalar multiplication.
             return a[0] * b[0];
         }
 
         final double[] prodHigh = new double[len];
         double prodLowSum = 0;

        for (int i = 0; i < len; i++) {
            final double ai = a[i];
            final double ca = SPLIT_FACTOR * ai;
            final double aHigh = ca - (ca - ai);
            final double aLow = ai - aHigh;

            final double bi = b[i];
            final double cb = SPLIT_FACTOR * bi;
            final double bHigh = cb - (cb - bi);
            final double bLow = bi - bHigh;
            prodHigh[i] = ai * bi;
            final double prodLow = aLow * bLow - (((prodHigh[i] -
                                                    aHigh * bHigh) -
                                                   aLow * bHigh) -
                                                  aHigh * bLow);
            prodLowSum += prodLow;
        }

        // if(len == 1)
        // {
        //     return a[0]*b[0];
        // }
        final double prodHighCur = prodHigh[0];
        // double prodHighNext = len > 1 ? prodHigh[1] : 0;
        double prodHighNext = prodHigh[1];
        // if(len == 1)
        // {
        //     return prodHighCur;
        // }
        double sHighPrev = prodHighCur + prodHighNext;
        double sPrime = sHighPrev - prodHighNext;
        double sLowSum = (prodHighNext - (sHighPrev - sPrime)) + (prodHighCur - sPrime);

        final int lenMinusOne = len - 1;
        for (int i = 1; i < lenMinusOne; i++) {
            prodHighNext = prodHigh[i + 1];
            final double sHighCur = sHighPrev + prodHighNext;
            sPrime = sHighCur - prodHighNext;
            sLowSum += (prodHighNext - (sHighCur - sPrime)) + (sHighPrev - sPrime);
            sHighPrev = sHighCur;
        }

        double result = sHighPrev + (prodLowSum + sLowSum);

        if (Double.isNaN(result)) {
            // either we have split infinite numbers or some coefficients were NaNs,
            // just rely on the naive implementation and let IEEE754 handle this
            result = 0;
            for (int i = 0; i < len; ++i) {
                result += a[i] * b[i];
            }
        }

        return result;
    }
```"""

EXAMPLE_OUTPUT_FUNC_DIFF = """```diff
@@ -5,7 +5,10 @@

              throw new DimensionMismatchException(len, b.length);
          }
  
+         if (len == 1) {
              // Revert to scalar multiplication.
+             return a[0] * b[0];
+         }
  
          final double[] prodHigh = new double[len];
          double prodLowSum = 0;
```"""



EXAMPLE_INPUT_FUNC_REPAIR = """public static double linearCombination(final double[] a, final double[] b)
        throws DimensionMismatchException {
        final int len = a.length;
        if (len != b.length) {
             throw new DimensionMismatchException(len, b.length);
         }
 
<Chunk_For_Modification>
             // Revert to scalar multiplication.
<Chunk_For_Modification>
 
         final double[] prodHigh = new double[len];
         double prodLowSum = 0;

        for (int i = 0; i < len; i++) {
            final double ai = a[i];
            final double ca = SPLIT_FACTOR * ai;
            final double aHigh = ca - (ca - ai);
            final double aLow = ai - aHigh;

            final double bi = b[i];
            final double cb = SPLIT_FACTOR * bi;
            final double bHigh = cb - (cb - bi);
            final double bLow = bi - bHigh;
            prodHigh[i] = ai * bi;
            final double prodLow = aLow * bLow - (((prodHigh[i] -
                                                    aHigh * bHigh) -
                                                   aLow * bHigh) -
                                                  aHigh * bLow);
            prodLowSum += prodLow;
        }

        // if(len == 1)
        // {
        //     return a[0]*b[0];
        // }
        final double prodHighCur = prodHigh[0];
        // double prodHighNext = len > 1 ? prodHigh[1] : 0;
        double prodHighNext = prodHigh[1];
        // if(len == 1)
        // {
        //     return prodHighCur;
        // }
        double sHighPrev = prodHighCur + prodHighNext;
        double sPrime = sHighPrev - prodHighNext;
        double sLowSum = (prodHighNext - (sHighPrev - sPrime)) + (prodHighCur - sPrime);

        final int lenMinusOne = len - 1;
        for (int i = 1; i < lenMinusOne; i++) {
            prodHighNext = prodHigh[i + 1];
            final double sHighCur = sHighPrev + prodHighNext;
            sPrime = sHighCur - prodHighNext;
            sLowSum += (prodHighNext - (sHighCur - sPrime)) + (sHighPrev - sPrime);
            sHighPrev = sHighCur;
        }

        double result = sHighPrev + (prodLowSum + sLowSum);

        if (Double.isNaN(result)) {
            // either we have split infinite numbers or some coefficients were NaNs,
            // just rely on the naive implementation and let IEEE754 handle this
            result = 0;
            for (int i = 0; i < len; ++i) {
                result += a[i] * b[i];
            }
        }

        return result;
    }"""

EXAMPLE_OUTPUT_FUNC_LOCATED = """```java
if (len == 1) {
```
```java
return a[0] * b[0];
}
```
"""

EXAMPLE_INPUT_FUNC_AGENT = """### Buggy function comment:
    /**
     * Compute a linear combination accurately.
     * This method computes the sum of the products
     * <code>a<sub>i</sub> b<sub>i</sub></code> to high accuracy.
     * It does so by using specific multiplication and addition algorithms to
     * preserve accuracy and reduce cancellation effects.
     * <br/>
     * It is based on the 2005 paper
     * <a href="http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.2.1547">
     * Accurate Sum and Dot Product</a> by Takeshi Ogita, Siegfried M. Rump,
     * and Shin'ichi Oishi published in SIAM J. Sci. Comput.
     *
     * @param a Factors.
     * @param b Factors.
     * @return <code>&Sigma;<sub>i</sub> a<sub>i</sub> b<sub>i</sub></code>.
     * @throws DimensionMismatchException if arrays dimensions don't match
     */

### Error message from JUnit test:
java.lang.ArrayIndexOutOfBoundsException: 1

### Failed JUnit test:
```java
    public void testLinearCombinationWithSingleElementArray() {
        final double[] a = { 1.23456789 };
        final double[] b = { 98765432.1 };

        Assert.assertEquals(a[0] * b[0], MathArrays.linearCombination(a, b), 0d);
    }
```

### Buggy function (You need to generate a fixed version of this program):
```java
public static double linearCombination(final double[] a, final double[] b) // **THIS IS LINE#0!**
        throws DimensionMismatchException {
        final int len = a.length;
        if (len != b.length) {
            throw new DimensionMismatchException(len, b.length);
        }

            // Revert to scalar multiplication.

        final double[] prodHigh = new double[len];
        double prodLowSum = 0;

        for (int i = 0; i < len; i++) {
            final double ai = a[i];
            final double ca = SPLIT_FACTOR * ai;
            final double aHigh = ca - (ca - ai);
            final double aLow = ai - aHigh;

            final double bi = b[i];
            final double cb = SPLIT_FACTOR * bi;
            final double bHigh = cb - (cb - bi);
            final double bLow = bi - bHigh;
            prodHigh[i] = ai * bi;
            final double prodLow = aLow * bLow - (((prodHigh[i] -
                                                    aHigh * bHigh) -
                                                   aLow * bHigh) -
                                                  aHigh * bLow);
            prodLowSum += prodLow;
        }


        final double prodHighCur = prodHigh[0];
        double prodHighNext = prodHigh[1];
        double sHighPrev = prodHighCur + prodHighNext;
        double sPrime = sHighPrev - prodHighNext;
        double sLowSum = (prodHighNext - (sHighPrev - sPrime)) + (prodHighCur - sPrime);

        final int lenMinusOne = len - 1;
        for (int i = 1; i < lenMinusOne; i++) {
            prodHighNext = prodHigh[i + 1];
            final double sHighCur = sHighPrev + prodHighNext;
            sPrime = sHighCur - prodHighNext;
            sLowSum += (prodHighNext - (sHighCur - sPrime)) + (sHighPrev - sPrime);
            sHighPrev = sHighCur;
        }

        double result = sHighPrev + (prodLowSum + sLowSum);

        if (Double.isNaN(result)) {
            // either we have split infinite numbers or some coefficients were NaNs,
            // just rely on the naive implementation and let IEEE754 handle this
            result = 0;
            for (int i = 0; i < len; ++i) {
                result += a[i] * b[i];
            }
        }

        return result;
    }
```"""

EXAMPLE_INPUT_FUNC_AGENT_DIFF = """### Buggy function comment:
    /**
     * Compute a linear combination accurately.
     * This method computes the sum of the products
     * <code>a<sub>i</sub> b<sub>i</sub></code> to high accuracy.
     * It does so by using specific multiplication and addition algorithms to
     * preserve accuracy and reduce cancellation effects.
     * <br/>
     * It is based on the 2005 paper
     * <a href="http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.2.1547">
     * Accurate Sum and Dot Product</a> by Takeshi Ogita, Siegfried M. Rump,
     * and Shin'ichi Oishi published in SIAM J. Sci. Comput.
     *
     * @param a Factors.
     * @param b Factors.
     * @return <code>&Sigma;<sub>i</sub> a<sub>i</sub> b<sub>i</sub></code>.
     * @throws DimensionMismatchException if arrays dimensions don't match
     */

### Error message from JUnit test:
java.lang.ArrayIndexOutOfBoundsException: 1

### Failed JUnit test:
```java
    public void testLinearCombinationWithSingleElementArray() {
        final double[] a = { 1.23456789 };
        final double[] b = { 98765432.1 };

        Assert.assertEquals(a[0] * b[0], MathArrays.linearCombination(a, b), 0d);
    }
```

### Buggy function (You need to generate a diff patch of this program):
```java
public static double linearCombination(final double[] a, final double[] b) // **THIS IS LINE#0!**
        throws DimensionMismatchException {
        final int len = a.length;
        if (len != b.length) {
            throw new DimensionMismatchException(len, b.length);
        }

            // Revert to scalar multiplication.

        final double[] prodHigh = new double[len];
        double prodLowSum = 0;

        for (int i = 0; i < len; i++) {
            final double ai = a[i];
            final double ca = SPLIT_FACTOR * ai;
            final double aHigh = ca - (ca - ai);
            final double aLow = ai - aHigh;

            final double bi = b[i];
            final double cb = SPLIT_FACTOR * bi;
            final double bHigh = cb - (cb - bi);
            final double bLow = bi - bHigh;
            prodHigh[i] = ai * bi;
            final double prodLow = aLow * bLow - (((prodHigh[i] -
                                                    aHigh * bHigh) -
                                                   aLow * bHigh) -
                                                  aHigh * bLow);
            prodLowSum += prodLow;
        }


        final double prodHighCur = prodHigh[0];
        double prodHighNext = prodHigh[1];
        double sHighPrev = prodHighCur + prodHighNext;
        double sPrime = sHighPrev - prodHighNext;
        double sLowSum = (prodHighNext - (sHighPrev - sPrime)) + (prodHighCur - sPrime);

        final int lenMinusOne = len - 1;
        for (int i = 1; i < lenMinusOne; i++) {
            prodHighNext = prodHigh[i + 1];
            final double sHighCur = sHighPrev + prodHighNext;
            sPrime = sHighCur - prodHighNext;
            sLowSum += (prodHighNext - (sHighCur - sPrime)) + (sHighPrev - sPrime);
            sHighPrev = sHighCur;
        }

        double result = sHighPrev + (prodLowSum + sLowSum);

        if (Double.isNaN(result)) {
            // either we have split infinite numbers or some coefficients were NaNs,
            // just rely on the naive implementation and let IEEE754 handle this
            result = 0;
            for (int i = 0; i < len; ++i) {
                result += a[i] * b[i];
            }
        }

        return result;
    }
```"""


HISTORY_DIFF_D4J = [
    {
        "role": "system",
        "content": DIFF_INSTRUCTION
    },
    {
        "role": "user",
        "content": EXAMPLE_INPUT_FUNC_AGENT_DIFF
    },
    {
        "role": "assistant",
        "content": EXAMPLE_OUTPUT_FUNC_DIFF
    },
]

HISTORY_BASE_D4J = [
        {
            "role": "system",
            "content": BASE_INSTRUCTION
        },
        {
            "role": "user",
            "content": EXAMPLE_INPUT_FUNC_REFINE
        },
        {
            "role": "assistant",
            "content": EXAMPLE_OUTPUT_FUNC_BASE
        },
]


HISTORY_LOCATED_D4J = [
        {
            "role": "system",
            "content": LOCATED_INSTRUCTION
        },
        {
            "role": "user",
            "content": EXAMPLE_INPUT_FUNC_REPAIR
        },
        {
            "role": "assistant",
            "content": EXAMPLE_OUTPUT_FUNC_LOCATED
        }
]

HISTORY_HYBRID_D4J = [
    {
        "role": "system",
        "content": HYBRID_INSTRUCTION
    },
    {
        "role": "user",
        "content": EXAMPLE_INPUT_FUNC_REPAIR
    },
    {
        "role": "assistant",
        "content": EXAMPLE_OUTPUT_FUNC_BASE
    }
]


HISTORY_GENERAL = [
    {
            "role": "system",
            "content": GENERAL_INSTRUCTION
    }
]

HISTORY_AGENT_D4J = [
    {
        "role": "system",
        "content": AGENT_INSTRUCTION
    },
    {
        "role": "user",
        "content": EXAMPLE_INPUT_FUNC_AGENT
    },
    {
        "role": "assistant",
        "content": EXAMPLE_OUTPUT_FUNC_BASE
    }
]


HISTORY_REVERSE_D4J = [
    {
        "role": "system",
        "content": REVERSE_INSTRUCTION
    },
    {
        "role": "user",
        "content": EXAMPLE_INPUT_FUNC_REPAIR
    },
    {
        "role": "assistant",
        "content": EXAMPLE_OUTPUT_FUNC_LOCATED
    }
]

HISTORY_FFID_D4J = [
    {
        "role": "system",
        "content": DIFF_INSTRUCTION
    },
    {
        "role": "user",
        "content": EXAMPLE_INPUT_FUNC_REPAIR
    },
    {
        "role": "assistant",
        "content": EXAMPLE_OUTPUT_FUNC_DIFF
    }
]
