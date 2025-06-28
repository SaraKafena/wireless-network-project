import math
import json
import os
import pandas as pd
import google.generativeai as genai
import traceback

from flask import Blueprint, request, jsonify

calculations_bp = Blueprint("calculations", __name__)

# =============================================================================
#  إعدادات LLM API - Google Gemini
# =============================================================================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def generate_ai_explanation(scenario, inputs, results):
    """Generate AI-powered explanation for the calculations using Google Gemini API."""
    prompt_content = f"""
Provide a detailed, user-friendly explanation for the following wireless network calculation scenario: {scenario.replace("_", " ").title()}.

User Inputs: {json.dumps(inputs, indent=2)}
Calculated Results: {json.dumps(results, indent=2)}

Explain the methodology, the significance of the results, and how they relate to the input parameters. Keep the explanation concise and easy to understand for someone with a basic understanding of wireless communications.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt_content)
        llm_output = response.text
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        llm_output = f"Failed to generate AI explanation using Gemini. Error: {e}. Please check your API key and network connection."
    
    return llm_output

@calculations_bp.route("/calculate/wireless", methods=["POST"])
def calculate_wireless():
    try:
        data = request.get_json()
        
        # Extract parameters
        bandwidth = float(data.get("bandwidth", 0))
        quantization_bits = int(data.get("quantization_bits", 0))
        source_encoder_bits = float(data.get("source_encoder_bits", 0))
        channel_encoder = float(data.get("channel_encoder", 0))
        interleaver_bits = int(data.get("interleaver_bits", 0))
        block_size = int(data.get("block_size", 0))
        overhead_per_block = int(data.get("overhead_per_block", 0))
        
        # Calculate rates at each stage
        sampler_output = bandwidth * 2  # Hz
        quantizer_output = sampler_output * quantization_bits  # bits/sec
        source_encoder_output = quantizer_output * source_encoder_bits  # bits/sec
        channel_encoder_output = source_encoder_output * (1 / channel_encoder)  # bits/sec
        interleaver_output = channel_encoder_output  # bits/sec (no change)
        number_of_blocks = interleaver_bits / block_size
        total_overhead_bit = number_of_blocks * overhead_per_block
        burst_formatting = interleaver_bits + total_overhead_bit  # bits/sec
        
        results = {
            "sampler_output": f"{sampler_output:,.0f} samples/sec",
            "quantizer_output": f"{quantizer_output:,.0f} bps",
            "source_encoder_output": f"{source_encoder_output:,.0f} bps",
            "channel_encoder_output": f"{channel_encoder_output:,.0f} bps",
            "interleaver_output": f"{interleaver_output:,.0f} bps",
            "burst_formatting": f"{burst_formatting:,.0f} bps"
        }
        
        explanation = generate_ai_explanation("wireless", data, results)
        
        return jsonify({
            "success": True,
            "results": results,
            "explanation": explanation
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@calculations_bp.route("/calculate/ofdm", methods=["POST"])
def calculate_ofdm():
    try:
        data = request.get_json()
        
        # Extract parameters
        bw_resource_block = float(data.get("bw_resource_block", 0))  # KHz
        subcarrier_spacing = float(data.get("subcarrier_spacing", 0))  # KHz
        ofdm_symbols = int(data.get("ofdm_symbols", 0))
        rb_duration = float(data.get("rb_duration", 0))  # msec
        modulated_bits = int(data.get("modulated_bits", 0))
        parallel_rb = int(data.get("parallel_rb", 0))
        
        # Calculate OFDM parameters
        data_rate_resource_element = math.log2(modulated_bits)  # bits/s
        bits_per_ofdm_symbol = (bw_resource_block / subcarrier_spacing) * data_rate_resource_element   # bits
        bits_per_resource_block = bits_per_ofdm_symbol * ofdm_symbols  # bits
        max_transmission = (parallel_rb * bits_per_resource_block) / (rb_duration / 1000)  # bits/sec
        spectral_efficiency = max_transmission / (bw_resource_block * 1000)  # bits/s/Hz
        
        results = {
            "data_rate_resource_element": f"{data_rate_resource_element:.2f} bits/s",
            "bits_per_ofdm_symbol": f"{bits_per_ofdm_symbol:.2f} bits",
            "bits_per_resource_block": f"{bits_per_resource_block:.2f} bits",
            "max_transmission": f"{max_transmission:.2f} bps",
            "spectral_efficiency": f"{spectral_efficiency:.2f} bits/s/Hz"
        }
        
        explanation = generate_ai_explanation("ofdm", data, results)
        
        return jsonify({
            "success": True,
            "results": results,
            "explanation": explanation
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@calculations_bp.route("/calculate/linkbudget", methods=["POST"])
def calculate_linkbudget():
    try:
        data = request.get_json()
        
        # Extract parameters
        ap_tx_power = float(data.get("access_point_transmit_power", 0))  # dBm
        ap_antenna_gain = float(data.get("access_point_antenna_gain", 0))  # dBi
        ap_rx_sensitivity = float(data.get("access_point_receive_sensitivity", 0))  # dBm
        client_tx_power = float(data.get("client_transmit_power", 0))  # dBm
        client_antenna_gain = float(data.get("client_antenna_gain", 0))  # dBi
        client_rx_sensitivity = float(data.get("client_receive_sensitivity", 0))  # dBm
        cable_loss_each_side = float(data.get("cable_loss_each_side", 0))  # dB
        distance_km = float(data.get("distance", 0))  # km
        frequency_ghz = float(data.get("frequency", 0))  # GHz

        # Convert distance to meters and frequency to Hz for FSPL calculation
        distance_m = distance_km * 1000
        frequency_hz = frequency_ghz * 1e9

        # Calculate Free Space Path Loss (FSPL) in dB
        fspl_db = 20 * math.log10(distance_m) + 20 * math.log10(frequency_hz) - 147.56

        # AP to Client Link
        eirp_ap = ap_tx_power + ap_antenna_gain - cable_loss_each_side
        rx_power_client = eirp_ap - fspl_db - cable_loss_each_side + client_antenna_gain
        link_margin_ap_to_client = rx_power_client - client_rx_sensitivity

        # Client to AP Link
        eirp_client = client_tx_power + client_antenna_gain - cable_loss_each_side
        rx_power_ap = eirp_client - fspl_db - cable_loss_each_side + ap_antenna_gain
        link_margin_client_to_ap = rx_power_ap - ap_rx_sensitivity

        # Determine Link Status
        link_reliable = "Yes" if link_margin_ap_to_client >= 0 and link_margin_client_to_ap >= 0 else "No"

        results = {
            "transmitted_power_ap": f"{ap_tx_power:.2f} dBm",
            "received_signal_strength_client": f"{rx_power_client:.2f} dBm",
            "transmitted_power_client": f"{client_tx_power:.2f} dBm",
            "received_signal_strength_ap": f"{rx_power_ap:.2f} dBm",
            "free_space_loss": f"{fspl_db:.2f} dB",
            "link_margin_ap_to_client": f"{link_margin_ap_to_client:.2f} dB",
            "link_margin_client_to_ap": f"{link_margin_client_to_ap:.2f} dB",
            "status": link_reliable
        }
        
        explanation = generate_ai_explanation("bidirectional_link_budget", data, results)
        
        return jsonify({
            "success": True,
            "results": results,
            "explanation": explanation
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@calculations_bp.route("/calculate/cellular", methods=["POST"])
def calculate_cellular():
    try:
        data = request.get_json()
        print(f"Received data for cellular calculation: {json.dumps(data, indent=2)}")

        # المسار المطلق لملف Erlang-B-Table.csv على نظام Windows
        erlang_table_path = "/home/ubuntu/wireless-network-complete-updated/wireless-network-backend/src/routes/Erlang-B-Table.csv"
        print(f"Attempting to load Erlang table from: {erlang_table_path}") # لغرض التتبع

        # Load Erlang B table from CSV
        erlang_table = pd.read_csv(erlang_table_path)
        print("Erlang table loaded successfully.") # لغرض التتبع
        
        # استخراج جميع المعاملات من النموذج، باستخدام المفاتيح التي تحتوي على شرطات سفلية لتتوافق مع JS
        time_slots_per_carrier = int(data.get("time_slots_per_carrier", 0))
        total_area = float(data.get("total_area", 0))  # m²
        max_number_of_users = int(data.get("max_number_of_users", 0))  # subscribers
        number_of_calls_per_day = int(data.get("number_of_calls_per_day", 0))  # calls per day
        call_duration = float(data.get("call_duration", 0))  # min
        gos = float(data.get("gos", 0))  # Grade of Service
        sir = float(data.get("sir", 0))  # Signal to Interference Ratio in dB
        p0 = float(data.get("p0", 0))  # P0 in dB
        receiver_sensitivity = float(data.get("receiver_sensitivity", 0))  # μW
        d0 = float(data.get("d0", 0))  # Reference Distance in meters
        path_loss_exponent = float(data.get("path_loss_exponent", 0))  # Path Loss Exponent
        co_channel_interferers = int(data.get("co_channel_interferers", 0))  # Number of Co-channel Interfering Cells
        
        # Convert dB to linear scale
        sir_watt = 10 ** (sir / 10)
        p0_watt = 10 ** (p0 / 10)
        
        # a) Maximum distance between transmitter and receiver
        if receiver_sensitivity == 0 or path_loss_exponent == 0:
            raise ValueError("Receiver sensitivity and path loss exponent cannot be zero.")
        max_distance = d0 * (p0_watt / receiver_sensitivity) ** (1 / path_loss_exponent)  # meter
        print(f"Calculated max_distance: {max_distance}") # لغرض التتبع
        
        # b) Maximum cell size (hexagonal)
        max_cell_size = (3 * math.sqrt(3) / 2) * (max_distance ** 2)  # m²
        print(f"Calculated max_cell_size: {max_cell_size}") # لغرض التتبع
        
        # c) Number of cells in the service area
        number_of_cells = total_area / max_cell_size if max_cell_size > 0 else 0
        print(f"Calculated number_of_cells: {number_of_cells}") # لغرض التتبع
        
        # d) Traffic load in the whole cellular system in Erlangs
        call_duration_sec = call_duration * 60  # Convert min to sec
        traffic_load_per_user = (number_of_calls_per_day * call_duration_sec) / (24 * 3600)  # Erlang per user
        traffic_load_system = traffic_load_per_user * max_number_of_users  # Total Erlang
        print(f"Calculated traffic_load_system: {traffic_load_system}") # لغرض التتبع
        
        # e) Traffic load in each cell in Erlangs
        traffic_load_cell = traffic_load_system / number_of_cells if number_of_cells > 0 else 0
        print(f"Calculated traffic_load_cell: {traffic_load_cell}") # لغرض التتبع
        
        # f) Number of cells in each cluster (based on co-channel interference)
        cluster_cells_real = ((sir_watt * co_channel_interferers) ** (2 / path_loss_exponent)) / 3  # Typically 7 for 6 co-channel interferers
        print(f"Calculated cluster_cells: {cluster_cells_real}") # لغرض التتبع

        valid_cluster_sizes = sorted({i**2 + i*j + j**2 for i in range(11) for j in range(11) if i**2 + i*j + j**2 > 0})

        # اختيار أقرب قيمة أكبر أو مساوية للناتج الحقيقي (أو fallback لأكبر واحدة إذا مافي ولا وحدة أكبر)
        cluster_cells = min((n for n in valid_cluster_sizes if n >= cluster_cells_real), default=max(valid_cluster_sizes))
        print(f"Closest valid cluster_cells (rounded to allowed values): {cluster_cells}")  # لغرض التتبع
            
        # g) Minimum number of carriers for the given QoS
        gos_columns = erlang_table.columns[1:]  # Exclude the 'N' column
        gos_values = [float(col.strip('%')) / 100 for col in gos_columns]
        
        # التحقق من أن gos ضمن النطاق الصحيح لتجنب الأخطاء
        if not (0 <= gos <= 1): # GOS عادة ما تكون بين 0 و 1 (0% إلى 100%)
            raise ValueError("Grade of Service (GOS) must be between 0 and 1.")

        closest_gos_idx = min(range(len(gos_values)), key=lambda i: abs(gos_values[i] - gos))
        gos_column = gos_columns[closest_gos_idx]
        
        channels_needed = 0
        # تأكد من أن traffic_load_cell ليس سالباً أو NaN
        if not erlang_table[erlang_table[gos_column] >= traffic_load_cell].empty and traffic_load_cell >= 0:
            channels_needed = erlang_table[erlang_table[gos_column] >= traffic_load_cell].index[0]
        else:
            print(f"Warning: traffic_load_cell ({traffic_load_cell}) is too high or invalid for the Erlang B table or GOS column '{gos_column}'. Defaulting channels_needed to max table length.")
            channels_needed = len(erlang_table) # Default to max channels if no match found
            
        min_carriers = math.ceil(channels_needed * cluster_cells / time_slots_per_carrier) if time_slots_per_carrier > 0 else 0
        print(f"Calculated min_carriers: {min_carriers}") # لغرض التتبع
        
        results = {
            "max_distance": f"{max_distance:.2f} meters",
            "max_cell_size": f"{max_cell_size:.2f} m²",
            "number_of_cells": f"{number_of_cells:,.0f} cells",
            "traffic_load_system": f"{traffic_load_system:.2f} Erlang",
            "traffic_load_cell": f"{traffic_load_cell:.2f} Erlang",
            "cluster_cells": f"{cluster_cells:.0f} cells",
            "min_carriers": f"{min_carriers} carriers"
        }
        
        explanation = generate_ai_explanation("cellular", data, results)
        
        return jsonify({
            "success": True,
            "results": results,
            "explanation": explanation
        })
        
    except Exception as e:
        print(f"Error in calculate_cellular: {e}") # اطبع الخطأ المحدد
        traceback.print_exc() # اطبع تتبع الخطأ الكامل
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
