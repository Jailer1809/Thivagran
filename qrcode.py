import streamlit as st
import qrcode
from io import BytesIO
import validators
from PIL import Image

st.set_page_config(page_title="QR Code Generator", page_icon="📱", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

st.title("QR Code Generator 📱")
st.write("Generate QR codes from any URL instantly!")

with st.sidebar:
    st.header("Customization Options")
    
    st.subheader("Colors")
    fg_color = st.color_picker("Foreground Color", "#000000", help="Color of the QR code pattern")
    bg_color = st.color_picker("Background Color", "#FFFFFF", help="Color of the QR code background")
    
    st.subheader("Size")
    box_size = st.slider("QR Code Size", min_value=5, max_value=20, value=10, help="Size of each box in pixels")
    border_size = st.slider("Border Size", min_value=1, max_value=10, value=4, help="Size of the border in boxes")
    
    st.subheader("Error Correction")
    error_correction = st.selectbox(
        "Error Correction Level",
        ["Low (7%)", "Medium (15%)", "Quartile (25%)", "High (30%)"],
        index=0,
        help="Higher levels allow the QR code to be read even if partially damaged"
    )
    
    error_correction_map = {
        "Low (7%)": qrcode.constants.ERROR_CORRECT_L,
        "Medium (15%)": qrcode.constants.ERROR_CORRECT_M,
        "Quartile (25%)": qrcode.constants.ERROR_CORRECT_Q,
        "High (30%)": qrcode.constants.ERROR_CORRECT_H
    }

tab1, tab2, tab3 = st.tabs(["Single URL", "Batch Generation", "Logo Embedding"])

with tab1:
    url_input = st.text_input(
        "Enter URL:",
        placeholder="https://example.com",
        help="Enter the URL you want to convert to a QR code"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        generate_button = st.button("Generate QR Code", type="primary", width='stretch')
    
    if generate_button:
        if not url_input:
            st.error("Please enter a URL first!")
        elif not validators.url(url_input):
            st.error("Please enter a valid URL (e.g., https://example.com)")
        else:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=error_correction_map[error_correction],
                    box_size=box_size,
                    border=border_size,
                )
                qr.add_data(url_input)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color=fg_color, back_color=bg_color)
                
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                
                st.session_state.history.insert(0, {
                    'url': url_input,
                    'image': buffer.getvalue(),
                    'settings': f"Size: {box_size}, Border: {border_size}, Error: {error_correction}"
                })
                if len(st.session_state.history) > 10:
                    st.session_state.history.pop()
                
                st.success("QR Code generated successfully!")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(buffer, caption=f"QR Code for: {url_input}")
                
                buffer.seek(0)
                st.download_button(
                    label="Download QR Code",
                    data=buffer,
                    file_name="qr_code.png",
                    mime="image/png",
                    width='stretch'
                )
                
            except Exception as e:
                st.error(f"An error occurred while generating the QR code: {str(e)}")

with tab2:
    st.subheader("Batch QR Code Generation")
    st.write("Enter multiple URLs (one per line) to generate QR codes in bulk.")
    
    batch_urls = st.text_area(
        "Enter URLs (one per line):",
        placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com",
        height=150
    )
    
    if st.button("Generate Batch QR Codes", type="primary"):
        if not batch_urls.strip():
            st.error("Please enter at least one URL!")
        else:
            urls = [url.strip() for url in batch_urls.split('\n') if url.strip()]
            valid_urls = []
            invalid_urls = []
            
            for url in urls:
                if validators.url(url):
                    valid_urls.append(url)
                else:
                    invalid_urls.append(url)
            
            if invalid_urls:
                st.warning(f"Skipping {len(invalid_urls)} invalid URL(s): {', '.join(invalid_urls[:3])}{'...' if len(invalid_urls) > 3 else ''}")
            
            if valid_urls:
                st.success(f"Generating {len(valid_urls)} QR code(s)...")
                
                cols = st.columns(3)
                for idx, url in enumerate(valid_urls):
                    try:
                        qr = qrcode.QRCode(
                            version=1,
                            error_correction=error_correction_map[error_correction],
                            box_size=box_size,
                            border=border_size,
                        )
                        qr.add_data(url)
                        qr.make(fit=True)
                        
                        img = qr.make_image(fill_color=fg_color, back_color=bg_color)
                        
                        buffer = BytesIO()
                        img.save(buffer, format="PNG")
                        buffer.seek(0)
                        
                        st.session_state.history.insert(0, {
                            'url': url,
                            'image': buffer.getvalue(),
                            'settings': f"Size: {box_size}, Border: {border_size}, Error: {error_correction}"
                        })
                        
                        with cols[idx % 3]:
                            st.image(buffer, caption=url[:30] + "..." if len(url) > 30 else url)
                            buffer.seek(0)
                            st.download_button(
                                label=f"Download {idx + 1}",
                                data=buffer,
                                file_name=f"qr_code_{idx + 1}.png",
                                mime="image/png",
                                key=f"batch_download_{idx}",
                                width='stretch'
                            )
                    except Exception as e:
                        st.error(f"Error generating QR code for {url}: {str(e)}")
                
                if len(st.session_state.history) > 10:
                    st.session_state.history = st.session_state.history[:10]

with tab3:
    st.subheader("QR Code with Logo")
    st.write("Upload a logo to embed in the center of your QR code.")
    
    logo_url = st.text_input(
        "Enter URL for logo embedding:",
        placeholder="https://example.com",
        help="The URL that the QR code will link to",
        key="logo_url"
    )
    
    logo_file = st.file_uploader("Upload Logo Image", type=["png", "jpg", "jpeg"], help="Upload a logo to place in the center of the QR code")
    
    if st.button("Generate QR Code with Logo", type="primary"):
        if not logo_url:
            st.error("Please enter a URL!")
        elif not validators.url(logo_url):
            st.error("Please enter a valid URL!")
        elif not logo_file:
            st.error("Please upload a logo image!")
        else:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=box_size,
                    border=border_size,
                )
                qr.add_data(logo_url)
                qr.make(fit=True)
                
                qr_img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert('RGB')
                
                logo = Image.open(logo_file).convert('RGBA')
                
                qr_width, qr_height = qr_img.size
                logo_size = qr_width // 5
                logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
                
                logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                
                qr_img.paste(logo, logo_pos, logo if logo.mode == 'RGBA' else None)
                
                buffer = BytesIO()
                qr_img.save(buffer, format="PNG")
                buffer.seek(0)
                
                st.session_state.history.insert(0, {
                    'url': logo_url,
                    'image': buffer.getvalue(),
                    'settings': f"With Logo, Size: {box_size}, Border: {border_size}"
                })
                if len(st.session_state.history) > 10:
                    st.session_state.history.pop()
                
                st.success("QR Code with logo generated successfully!")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(buffer, caption=f"QR Code with Logo for: {logo_url}")
                
                buffer.seek(0)
                st.download_button(
                    label="Download QR Code with Logo",
                    data=buffer,
                    file_name="qr_code_with_logo.png",
                    mime="image/png",
                    width='stretch'
                )
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if st.session_state.history:
    st.divider()
    st.header("Recent QR Codes")
    
    cols = st.columns(5)
    for idx, item in enumerate(st.session_state.history[:10]):
        with cols[idx % 5]:
            st.image(item['image'])
            st.caption(item['url'][:25] + "..." if len(item['url']) > 25 else item['url'])
            st.caption(item['settings'], help="Generation settings")
            st.download_button(
                label="Download",
                data=item['image'],
                file_name=f"qr_code_history_{idx}.png",
                mime="image/png",
                key=f"history_download_{idx}",
                width='stretch'
            )

st.divider()
st.markdown("### How to use:")
st.markdown("""
1. *Single URL*: Enter a URL and generate a customized QR code
2. *Batch Generation*: Enter multiple URLs (one per line) to generate multiple QR codes at once
3. *Logo Embedding*: Upload a logo to embed in the center of your QR code
4. *Customization*: Use the sidebar to customize colors, size, and error correction level
5. *History*: View and download your recently generated QR codes
""")
