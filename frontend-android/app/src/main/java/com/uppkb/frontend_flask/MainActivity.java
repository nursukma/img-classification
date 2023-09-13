package com.uppkb.frontend_flask;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import android.Manifest;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.provider.OpenableColumns;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.ArrayList;
import java.util.Enumeration;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity {
    final int SELECT_IMAGES = 1;
    final int CAMERA_REQUEST = 2;
    final int MY_CAMERA_PERMISSION_CODE = 200;

    ArrayList<Uri> selectedPaths;
    boolean selectedImages = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.CAMERA}, 2);
        ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.READ_EXTERNAL_STORAGE}, 1);

        setContentView(R.layout.activity_main);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        switch (requestCode){
            case 1:
                if(grantResults.length > 0&& grantResults[0] == PackageManager.PERMISSION_GRANTED) {
//                    Toast.makeText(getApplicationContext(), "Access to Storage Permission Granted.", Toast.LENGTH_SHORT).show();
                } else {
//                    Toast.makeText(getApplicationContext(), "Access to Storage Permission Denied.", Toast.LENGTH_SHORT).show();
                }
                return;
            case 2:
                if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
//                    Toast.makeText(this, "Camera Permission Granted.", Toast.LENGTH_LONG).show();
                }
                else {
                    Toast.makeText(this, "Izin kamera ditolak", Toast.LENGTH_SHORT).show();
                }
                return;
        }
    }

    public static String getIPAddress() {
        try {
            Enumeration<NetworkInterface> networkInterfaces = NetworkInterface.getNetworkInterfaces();
            while (networkInterfaces.hasMoreElements()) {
                NetworkInterface networkInterface = networkInterfaces.nextElement();
                Enumeration<InetAddress> inetAddresses = networkInterface.getInetAddresses();
                while (inetAddresses.hasMoreElements()) {
                    InetAddress inetAddress = inetAddresses.nextElement();
                    if (!inetAddress.isLoopbackAddress() && inetAddress.getHostAddress().indexOf(':') == -1) {
                        return inetAddress.getHostAddress();
                    }
                }
            }
        } catch (SocketException e) {
            e.printStackTrace();
        }
        return null;
    }

    public void connectServer(View v){
        TextView responseText = findViewById(R.id.responseText);
        if(selectedImages == false){
            responseText.setText("Silakan pilih gambar dulu.");
            return;
        }

        responseText.setText("Loading ...");

        String ipAddress = "192.168.18.187";
        String postURL = "http://"+ipAddress+":5000"+"/predict";

        MultipartBody.Builder multipartBuilder = new MultipartBody.Builder().setType(MultipartBody.FORM);
        byte[] byteArray = null;

        try {
            InputStream inputStream = getContentResolver().openInputStream(selectedPaths.get(0));
            ByteArrayOutputStream byteBuffer = new ByteArrayOutputStream();
            int buffersize = 2048;
            byte[] buffer = new byte[buffersize];

            int len = 0;
            while((len = inputStream.read(buffer)) != -1){
                byteBuffer.write(buffer, 0, len);
            }
            byteArray = byteBuffer.toByteArray();
        }catch (Exception e){
            Log.d("ERROR: ","GAMBAR FAIL");
            Toast.makeText(this, "Silakan pilih gambar", Toast.LENGTH_SHORT).show();
            return;
        }

        multipartBuilder.addFormDataPart("file","input.jpg", RequestBody.create(MediaType.parse("image/*jpg"),byteArray));
        RequestBody postBodyImage = multipartBuilder.build();
        postRequest(postURL,postBodyImage);
    }

    private void postRequest(String postURL, RequestBody postBodyImage) {
        OkHttpClient client = new OkHttpClient();
        Request request = new Request.Builder().url(postURL).post(postBodyImage).build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                call.cancel();
                Log.d("Upload gagal: ",e.getMessage());

                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Toast.makeText(MainActivity.this, "Gagal menyambungkan ke server", Toast.LENGTH_LONG).show();
                    }
                });
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                String responseBody = response.body().string();
                TextView responseText = findViewById(R.id.responseText);
                try {
                    JSONObject jsonObject = new JSONObject(responseBody);
                    String status = jsonObject.getString("status");
                    JSONObject predictionsObject = jsonObject.getJSONObject("prediksi");
                    String predictionText = predictionsObject.getString("class1");

                    JSONArray jsonArray = predictionsObject.getJSONArray("prob1");
                    StringBuilder rekomendasi = new StringBuilder();

                    for (int i = 0; i < jsonArray.length(); i++) {
                        if (i > 0) {
                            rekomendasi.append(", "); // Add a comma and space between values
                        }
                        rekomendasi.append(jsonArray.getString(i));
                    }
                    // Update UI in the main thread
                    if(status.equals("success")) {
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                responseText.setText("Hasil prediksi: "+predictionText+"\n"+
                                        "Rekomendasi: \n"+rekomendasi.toString());
                            }
                        });
                    }
                    else{
                        Log.d("Server Response: ", response.body().toString());
                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                responseText.setText("Terjadi kesalahan, coba ulangi");
                            }
                        });
                    }

                } catch (JSONException e) {
                    // Handle JSON parsing error
                }
            }
        });
    }

    public void captureImage(View v) {
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.CAMERA}, MY_CAMERA_PERMISSION_CODE);
        }
        else {
            Intent cameraIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
            startActivityForResult(cameraIntent, CAMERA_REQUEST);
        }
    }

    public void selectImage(View v) {
        Intent intent = new Intent();
        intent.setType("image/*");
        intent.setAction(Intent.ACTION_GET_CONTENT);
        startActivityForResult(Intent.createChooser(intent, "Pilih gambar"), SELECT_IMAGES);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        try {
            if(requestCode == SELECT_IMAGES && resultCode == RESULT_OK && data != null){
                selectedPaths = new ArrayList<>();
                ImageView imgView = findViewById(R.id.imageView);
                TextView imgName = findViewById(R.id.nama_file);

                if (data.getData() != null) {
                    Uri uri = data.getData();
                    Log.d("ImageDetails", "URI : " + uri);
                    selectedPaths.add(uri);
                    selectedImages = true;
                    imgName.setText(getFileName(selectedPaths.get(0)));
                    imgView.setImageURI(selectedPaths.get(0));
                }
            } else if (requestCode == CAMERA_REQUEST && resultCode == RESULT_OK && data != null) {
                selectedPaths = new ArrayList<>();
                TextView imgName = findViewById(R.id.nama_file);
                ImageView imgView = findViewById(R.id.imageView);

                if (data.getExtras().get("data") != null) {
                    Bitmap photo = (Bitmap) data.getExtras().get("data");
                    Uri uri = getImageUri(getApplicationContext(), photo);
                    Log.d("ImageDetails", "URI : " + uri);
                    selectedPaths.add(uri);
                    selectedImages = true;
                    imgName.setText(getFileName(selectedPaths.get(0)));
                    imgView.setImageURI(selectedPaths.get(0));
                }
            } else {
                Toast.makeText(this, "Silakan pilih gambar terlebih dahulu", Toast.LENGTH_LONG).show();
            }
        }catch (Exception e){
            Toast.makeText(this, "Terjadi kesalahan!", Toast.LENGTH_LONG).show();
            Log.d("Error",e.getMessage());
        }
    }

    public Uri getImageUri(Context inContext, Bitmap inImage) {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        inImage.compress(Bitmap.CompressFormat.JPEG, 100, bytes);
        String path = MediaStore.Images.Media.insertImage(inContext.getContentResolver(), inImage, "Nama File", null);
        return Uri.parse(path);
    }

    @SuppressLint("Range")
    public String getFileName(Uri uri) {
        String result = null;
        if (uri.getScheme().equals("content")) {
            Cursor cursor = getContentResolver().query(uri, null, null, null, null);
            try {
                if (cursor != null && cursor.moveToFirst()) {
                    result = cursor.getString(cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME));
                }
            } finally {
                cursor.close();
            }
        }
        if (result == null) {
            result = uri.getPath();
            int cut = result.lastIndexOf('/');
            if (cut != -1) {
                result = result.substring(cut + 1);
            }
        }
        return result;
    }
}