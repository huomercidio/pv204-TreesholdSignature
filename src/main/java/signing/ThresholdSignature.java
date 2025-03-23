package signing;

import event.NostrEvent;

import java.nio.charset.StandardCharsets;
import java.security.*;

public class ThresholdSignature {

    public static byte[] signEvent(NostrEvent event, PrivateKey privateKey) throws NoSuchAlgorithmException, InvalidKeyException, SignatureException {
        Signature signature = Signature.getInstance("SHA256withECDSA");
        signature.initSign(privateKey);
        signature.update(event.getContentHash().getBytes(StandardCharsets.UTF_8));
        return signature.sign();
    }
}