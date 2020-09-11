import java.util.HashMap;
import java.util.Scanner;

class Coins {

    public long max(long n) {
        HashMap<Long, Long> map= new HashMap<>();
        return maxHelper(n, map);
    }

    public long maxHelper(long n, HashMap<Long, Long> map) {
        if (n < 12) return n;
        else {
            if (map.containsKey(n)) return map.get(n);
            long a= maxHelper(n / 2, map);
            long b= maxHelper(n / 3, map);
            long c= maxHelper(n / 4, map);
            long sum= a + b + c;
            if (sum > n) {
                map.put(n, sum);
                return sum;
            }
            map.put(n, n);
            return n;
        }
    }

    public static void main(String args[]) {
        Scanner scan= new Scanner(System.in);
        Coins coins= new Coins();
        while (scan.hasNext()) {
            long num= scan.nextLong();
            System.out.println(coins.max(num));
        }
        scan.close();
    }
}
