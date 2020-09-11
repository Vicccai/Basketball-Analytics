import java.util.Arrays;
import java.util.Scanner;

class Cows {
    public static void main(String args[]) {
        Scanner scan= new Scanner(System.in);
        int testCases= scan.nextInt();
        StringBuilder str= new StringBuilder();
        for (int i= 0; i < testCases; i++ ) {
            int numStalls= scan.nextInt();
            int numCows= scan.nextInt();
            int[] stalls= new int[numStalls];
            for (int j= 0; j < numStalls; j++ ) {
                stalls[j]= scan.nextInt();
            }
            int largestMin= largestMinDist(numStalls, numCows, stalls);
            str.append(largestMin + "\n");

        }
        scan.close();
        System.out.println(str);
    }

    public static int largestMinDist(int numStalls, int numCows, int[] stalls) {
        Arrays.sort(stalls);
        int low= 0;
        int high= stalls[numStalls - 1];
        int max= -1;
        while (low < high) {
            int mid= (low + high) / 2;
            if (enoughCows(mid, numStalls, numCows, stalls)) {
                if (mid > max) max= mid;
                low= low + 1;
            } else {
                high= mid;
            }
        }
        return max;
    }

    public static boolean enoughCows(int mid, int numStalls, int numCows, int[] stalls) {
        int pivot= 0;
        int cows= 1;
        for (int i= 1; i < numStalls; i++ ) {
            if (stalls[i] - stalls[pivot] >= mid) {
                cows++ ;
                pivot= i;
                if (cows == numCows) return true;
            }
        }
        return false;
    }
}
