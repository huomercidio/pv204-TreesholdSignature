package signing;

import event.NostrEvent;
import keymanagement.KeyGeneration;
import keymanagement.KeyManager;

import java.math.BigInteger;
import java.security.KeyPair;
import java.security.PublicKey;
import java.time.Instant;
import java.util.Map;
import java.util.logging.Logger;

public class AutomaticSigner {

    private static final Logger logger = Logger.getLogger(AutomaticSigner.class.getName());

    private final PublicKey publicKey;
    private final long signingIntervalStart;
    private final long signingIntervalEnd;
    private final Map<Integer, BigInteger> shares;

    public AutomaticSigner(int totalShares, int threshold, long signingIntervalStart, long signingIntervalEnd) throws Exception {
        KeyPair keyPair = KeyManager.generateKeyPair();
        this.publicKey = keyPair.getPublic();
        this.shares = KeyGeneration.generateShares(new BigInteger("123456789"), totalShares, threshold); // Example secret
        this.signingIntervalStart = signingIntervalStart;
        this.signingIntervalEnd = signingIntervalEnd;
        logger.info("Automatic signer initialized.");
    }

    public BigInteger generatePartialSignature(NostrEvent event) throws Exception {
        long currentTime = Instant.now().getEpochSecond();
        if (currentTime >= signingIntervalStart && currentTime <= signingIntervalEnd) {
            BigInteger nonce = FrostThresholdSignature.generateNonce();
            BigInteger partialSignature = FrostThresholdSignature.generatePartialSignature(event, shares.get(1), nonce);
            logger.info("Generated partial signature for event: " + event.getId());
            return partialSignature;
        } else {
            throw new IllegalStateException("Automatic signer is inactive. Try again later.");
        }
    }

    public PublicKey getPublicKey() {
        return publicKey;
    }
}