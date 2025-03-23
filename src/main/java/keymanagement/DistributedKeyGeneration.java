package keymanagement;

import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.Map;

public class DistributedKeyGeneration {

    private static final BigInteger PRIME = new BigInteger("208351617316091241234326746312124448251235562226470491514186331217050270460481");

    public static Map<Integer, BigInteger> generateShares(int totalShares, int threshold) {
        SecureRandom random = new SecureRandom();
        BigInteger secret = new BigInteger(PRIME.bitLength(), random).mod(PRIME); // Collaborative secret
        return KeyGeneration.generateShares(secret, totalShares, threshold);
    }
}